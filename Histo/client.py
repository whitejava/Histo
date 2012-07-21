import os, io, sys, pchex, imaplib
from stream import objectstream, copy, tcpstream, hashstream
from timetuple import totuple
from datetime import datetime

def main():
    command = sys.argv[1]
    t = {'browser': browser,
         'commitunpack': commitunpack}
    t[command](sys.argv[2:])

def browser(address, extractpath):
    print('Search:')
    keyword = os.sys.stdin.readline()[:-1]
    result = search(address, keyword)
    showresult(result)
    selections = [int(e) for e in os.sys.stdin.readline()[:-1].split()]
    for select in selections:
        item = result[select]
        name = item['name']
        time = '%04d%02d%02d%02d%02d%02d' % item['datetime'][:6]
        path = os.path.join(extractpath, time + name)
        if os.path.exists(path):
            print(name + ' is exist, pass')
        else:
            print('Downloading: ' + name)
            download(address, item['range'], path)

def netclient(x):
    def a(ip, port, *k, **kw):
        stream = objectstream(tcpstream((ip, port)))
        return x(stream, *k, **kw)
    return a

@netclient
def commitunpack(stream, path, compress):
    compress = {'compress':True, 'nocompress':False}[compress]
    for e in 'commitunpack', path, compress:
        stream.writeobject(e)
    assert stream.readobject() == 'ok'

def showresult(result):
    for i,e in enumerate(result):
        time = '%04d-%02d%02d' % (e['datetime'][:3])
        name = e['name']
        print('%d %s %s' % (i, time, name))

@netclient
def search(stream, keyword):
    for e in 'search', keyword:
        stream.writeobject(e)
    return stream.readobject()

@netclient
def download(stream, range, path):
    assert not os.path.exists(path)
    for e in 'get', range:
        stream.writeobject(e)
    length = range[1] - range[0]
    with open(path, 'wb') as f:
        copy(stream, f, length)

def main():
    ip = sys.argv[1]
    port = int(sys.argv[2])
    command = sys.argv[3]
    c = client((ip, port))
    t = {'browser': c.browser,
         'md5all': c.md5all,
         'markduplication': c.markduplication,
         'commitunpack': c.commitunpack,
         'commitold': c.commitold}
    t[command](*sys.argv[4:])
    print('ok')

class client:
    def __init__(self, address):
        self._address = address
    
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
        time = selection['datetime']
        time = '%04d%02d%02d%02d%02d%02d' % time[:6]
        path = os.path.join(extractpath, time + name)
        if os.path.exists(path):
            print(path, 'is exist!')
            return
        print('Downloading', name)
        with open(path, 'wb') as f:
            self.get(range, f)
        print(path)
    
    def md5all(self, outputpath):
        result = self.search('')
        with open(outputpath, 'w', encoding='utf8') as f:
            for e in result:
                s = hashstream('md5')
                self.get(e['range'], s)
                md5 = pchex.encode(s.digest())
                name = '-'.join([str(j) for j in e['datetime']])
                print(name, md5, file=f)
                print(name, md5)
    
    def markduplication(self, username, password):
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(username + '@gmail.com', password)
        imap.list()
        imap.select('inbox')
        mails = imap.search(None, 'ALL')
        mails = mails[1][0]
        mails = str(mails, 'utf8').split()
        mails = ','.join(mails)
        subjects = imap.fetch(mails, '(BODY.PEEK[HEADER.FIELDS (SUBJECT)])')
        subjects = subjects[1]
        result = []
        for e in subjects:
            if type(e) is not tuple:
                continue
            uid = str(e[0].split()[0],'utf8')
            subject = str(e[1].split()[1],'utf8')
            result.append((subject, uid))
        
        result = list(sorted(result))
        delete = []
        for i in range(1, len(result)):
            if result[i][0] == result[i-1][0]:
                delete.append(result[i])
        delete = ','.join([e[1] for e in delete])
        imap.store(delete, '+FLAGS', '\\Seen')
    
    def commitunpack(self, path, compress):
        compress = {'compress': True, 'nocompress': False}[compress]
        stream = objectstream(tcpstream(self._address))
        stream.writeobject('commitunpack')
        stream.writeobject(path)
        stream.writeobject(compress)
        assert stream.readobject() == 'ok'
    
    def search(self, keyword):
        stream = tcpstream(self._address)
        stream = objectstream(stream)
        stream.writeobject('search')
        stream.writeobject(keyword)
        return stream.readobject()
    
    def get(self, range, output):
        stream = tcpstream(self._address)
        stream = objectstream(stream)
        stream.writeobject('get')
        stream.writeobject(range)
        length = range[1] - range[0]
        result = stream.readobject()
        if result == 'data':
            assert copy(stream, output, length) == length
        elif result == 'missing':
            missing = stream.readobject()
            raise Exception('missing: ' + ' '.join([str(e) for e in missing]))
    
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
    
    def commitold(self, path):
        self.localcommitallv1(os.path.join(path, 'v1'))
        self.localcommitallv2(os.path.join(path, 'v2'))
    
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

def showsearchresult(a):
    for i,e in enumerate(a):
        time = e['datetime']
        time = time[:3]
        time = '{:04}-{:02d}{:02d}'.format(*time)
        name = e['name']
        print(i, time, name)

if __name__ == '__main__':
    main()