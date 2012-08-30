import os, sys
from pclib import objectstream, tcpstream

def main():
    try:
        command = sys.argv[1]
        t = {'browser': browser,
             'commitunpack': commitunpack}
        t[command](*sys.argv[2:])
    except Exception as e:
        print(e)
        input()

def browser(ip, port, extractpath):
    print('Search:')
    keyword = os.sys.stdin.readline()[:-1]
    result = search(ip, port, keyword)
    showresult(result)
    selections = [int(e) for e in os.sys.stdin.readline()[:-1].split()]
    for select in selections:
        commitid = result['CommitID']
        item = result[select]
        name = item['Name']
        time = '%04d%02d%02d%02d%02d%02d' % item['Time'][:6]
        path = os.path.join(extractpath, time + name)
        if os.path.exists(path):
            print(name + ' is exist, pass')
        else:
            print('Downloading: %d' % commitid)
            download(ip, port, commitid, path)

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
def download(stream, commitid, path):
    assert not os.path.exists(path)
    stream.writeobject(commitid)
    assert stream.readobject() == 'ok'

if __name__ == '__main__':
    main()