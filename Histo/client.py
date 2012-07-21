import os, sys
from stream import objectstream, copy, tcpstream

def main():
    command = sys.argv[1]
    t = {'browser': browser,
         'commitunpack': commitunpack}
    t[command](*sys.argv[2:])

def browser(ip, port, extractpath):
    print('Search:')
    keyword = os.sys.stdin.readline()[:-1]
    result = search(ip, port, keyword)
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
            download(ip, port, item['range'], path)

def netclient(x):
    def a(ip, port, *k, **kw):
        stream = objectstream(tcpstream((ip, int(port))))
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

if __name__ == '__main__':
    main()