import os, sys
from pclib import objectstream, tcpstream

def main():
    try:
        command = sys.argv[1]
        t = {'browser': browser,
             'commit': commit}
        t[command](*sys.argv[2:])
    except Exception as e:
        raise

def browser(ip, port):
    print('Search:')
    keyword = os.sys.stdin.readline()[:-1]
    result = search(ip, port, keyword)
    showresult(result)
    print('Input selection(s):')
    selections = [int(e) for e in os.sys.stdin.readline()[:-1].split()]
    for select in selections:
        select = result[select]
        commitid = select['CommitID']
        print('Downloading: %d' % commitid)
        try:
            download(ip, port, commitid)
        except Exception:
            print('Fail: %d' % commitid)

def netclient(x):
    def a(ip, port, *k, **kw):
        stream = objectstream(tcpstream((ip, int(port))))
        return x(stream, *k, **kw)
    return a

@netclient
def commit(stream, path, compress):
    stream.writeobject('commit')
    compress = {'compress':True, 'nocompress':False}[compress]
    p = dict()
    p['Path'] = path
    p['Compress'] = compress
    p['Time'] = None
    stream.writeobject(p)
    assert stream.readobject() == 'ok'

def showresult(result):
    for i,e in reversed(list(enumerate(result))):
        time = '%04d-%02d%02d' % (e['Time'][:3])
        commitid = e['CommitID']
        name = e['Name']
        print('%d %d %s %s' % (i, commitid, time, name))

@netclient
def search(stream, keyword):
    for e in 'search', keyword:
        stream.writeobject(e)
    return stream.readobject()

@netclient
def download(stream, commitid):
    stream.writeobject('get')
    stream.writeobject(commitid)
    assert stream.readobject() == 'ok'

if __name__ == '__main__':
    main()