__all__ = ['commitfile', 'commitprevious']

import os, io, sys, pickle
from stream import objectstream, copy, tcpstream
from timetuple import totuple
from datetime import datetime
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
    t = {'commit': c.commitfile,
         'commitallv1': c.commitallv1,
         'commitallv2': c.commitallv2,
         'commitv1': c.commitv1,
         'commitv2': c.commitv2,
         'search': lambda *k:showsearchresult(c.search(*k)),
         'browser': c.browser,
         'get': c.get}
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
    
    def commitfile(self, name, path, time = None):
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
        for e in os.listdir(path):
            self.commitv1(os.path.join(path, e))
    
    def commitallv2(self, path):
        for e in os.listdir(path):
            self.commitv2(os.path.join(path, e))
    
    def commitv1(self, filename):
        time, name = _resolvefilename(filename)
        self.commitfile(name, filename, time = time)
    
    def commitv2(self, path):
        name = os.path.dirname(path)
        time = name[:19]
        time = time.split()
        time = [int(e) for e in time]
        time += [0]
        name = name[20:]
        self.commitfile(name, path, time = time)
        
    
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
        with open(path, 'wb') as f:
            assert copy(stream, f, length) == length
    
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

def _cut(string, pieces):
    #Stream
    string = io.StringIO(string)
    #Read pieces
    return [string.read(e) for e in pieces]

def _resolvefilename(filename):
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