__all__ = ['commitfile', 'commitprevious']

import os, io, sys, pickle
from stream import objectstream, copy, tcpstream
from timetuple import totuple
from datetime import datetime
import shutil

usage = '''\
histo.client ip[:port] command[ parameter1[ parameter2[...]]]
command can be one of following values:
commitfile        name
                  path
                  
commitv1          path

commitv2          path

search            keyword

get               start
                  end
                  output path

For example:
histo.client 192.168.1.2:13750 commitfile Test /home/username/test.rar
'''

def main():
    print(usage)
    address = sys.argv[1]
    address = address.split(':')
    ip = address[0]
    port = 13750
    if len(address) > 1:
        port = int(address[1])
    address = (ip, port)
    c = client(address)
    t = {'commit': c.commit,
         'commitallv1': c.commitallv1,
         'commitallv2': c.commitallv2,
         'commitv1': c.commitv1,
         'commitv2': c.commitv2,
         'localcommit': c.localcommit,
         'localcommitallv1': c.localcommitallv1,
         'localcommitallv2': c.localcommitallv2,
         'localcommitmix':c.localcommitmix,
         'search': lambda *k:showsearchresult(c.search(*k)),
         'browser': c.browser,
         'get': c.get,
         'upload': c.upload}
    command = sys.argv[2]
    t[command](*sys.argv[3:])
    print('ok')

def showsearchresult(a):
    for i,e in enumerate(a):
        time = e['datetime']
        time = time[:3]
        time = '{:04}-{:02d}{:02d}'.format(*time)
        name = e['name']
        print(i, time, name)

class client:
    def __init__(self, address):
        self._address = address
    
    def commit(self, name, path, time = None):
        stream = tcpstream(self._address)
        stream = objectstream(stream)
        lastmodify = totuple(datetime.fromtimestamp(os.path.getmtime(path)))
        filesize = os.path.getsize(path)
        stream.writeobject('commit')
        stream.writeobject(time)
        stream.writeobject(name)
        stream.writeobject(lastmodify)
        stream.writeobject(os.path.basename(path))
        stream.writeobject(filesize)
        with open(path, 'rb') as f:
            assert copy(f, stream, filesize) == filesize
        print('client send finish')
        assert stream.readobject() == 'ok'
    
    def commitallv1(self, path):
        for e in sorted(os.listdir(path)):
            self.commitv1(os.path.join(path, e))
    
    def commitallv2(self, path):
        for e in sorted(os.listdir(path)):
            self.commitv2(os.path.join(path, e))
    
    def commitv1(self, filename):
        time, name = resolvev1(filename)
        self.commitfile(name, filename, time = time)
    
    def commitv2(self, path):
        time, name = resolvev2(path)
        self.commitfile(name, path, time = time)
    
    def localcommit(self, name, path, time = None):
        stream = objectstream(tcpstream(self._address))
        stream.writeobject('localcommit')
        stream.writeobject(time)
        stream.writeobject(name)
        stream.writeobject(path)
        assert stream.readobject() == 'ok'
        self._fakedelete(path)
    
    def _fakedelete(self, path):
        dest = os.path.join('G:\\delete', os.path.basename(path))
        os.rename(path, dest)
    
    def localcommitallv1(self, root):
        for e in sorted(os.listdir(root)):
            self.localcommitv1(os.path.join(root, e))
    
    def localcommitallv2(self, root):
        for e in sorted(os.listdir(root)):
            self.localcommitv2(os.path.join(root, e))
    
    def localcommitv1(self, path):
        time, name = resolvev1(path)
        self.localcommit(name, path, time)
    
    def localcommitv2(self, path):
        time, name = resolvev2(path)
        self.localcommit(name, path, time)
    
    def localcommitmix(self, path):
        self.localcommitallv1(os.path.join(path, 'v1'))
        self.localcommitallv2(os.path.join(path, 'v2'))
    
    def search(self, keyword):
        stream = tcpstream(self._address)
        stream = objectstream(stream)
        stream.writeobject('search')
        stream.writeobject(keyword)
        return stream.readobject()
    
    def get(self, range, path):
        stream = tcpstream(self._address)
        stream = objectstream(stream)
        stream.writeobject('get')
        stream.writeobject(range)
        length = range[1] - range[0]
        result = stream.readobject()
        if result == 'data':
            assert not os.path.exists(path)
            with open(path, 'wb') as f:
                assert copy(stream, f, length) == length
        elif result == 'missing':
            missing = stream.readobject()
            raise Exception('missing: ' + ' '.join([str(e) for e in missing]))
    
    def browser(self, extractpath):
        print('Input to search:');
        keyword = os.sys.stdin.readline()
        keyword = keyword[:-1]
        result = self.search(keyword)
        showsearchresult(result)
        selection = os.sys.stdin.readline()
        selection = selection[:-1]
        selection = int(selection)
        selection = result[selection]
        range = selection['range']
        name = selection['name']
        path = os.path.join(extractpath, name)
        print('Downloading', path)
        self.get(range, path)
        print(path)
    
    def upload(self, root):
        for e in os.listdir(root):
            type = {'i':'index','d':'data','u':'usage'}[e[0]]
            path = os.path.join(root, e)
            with open(path, 'rb') as f:
                data = f.read()
            stream = tcpstream(self._address)
            stream = objectstream(stream)
            stream.writeobject('upload')
            stream.writeobject(type)
            stream.writeobject(e)
            stream.writeobject(data)
            assert stream.readobject() == 'ok'

def _cut(string, pieces):
    #Stream
    string = io.StringIO(string)
    #Read pieces
    return [string.read(e) for e in pieces]

def resolvev2(filename):
    name = os.path.basename(filename)
    time = name[:19]
    time = time.split('-')
    time = [int(e) for e in time]
    time += [0]
    time = tuple(time)
    name = name[20:]
    return time, name

def resolvev1(filename):
    #Base name
    filename = os.path.basename(filename)
    #Extract datetime, name
    datetime, name = filename[:12], filename[12:]
    #Tuple datetime
    datetime = tuple([int(e) for e in _cut(datetime,[4,2,2,2,2])] + [0,0])
    #Strip underline in name
    if name.startswith('_'): name = name[1:]
    #Return
    return datetime, name

if __name__ == '__main__':
    main()