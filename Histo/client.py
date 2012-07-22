import os, sys, imaplib
from stream import objectstream, copy, tcpstream

def main():
    try:
        command = sys.argv[1]
        t = {'browser': browser,
             'commitunpack': commitunpack,
             'markdup': markdup}
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

def markdup(username, password):
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    imap.login(username + '@gmail.com', password)
    imap.list()
    imap.select('inbox')
    mails = str(imap.search(None, 'ALL')[1][0],'utf8').split()
    subjects = imap.fetch(','.join(mails), '(BODY.PEEK[HEADER.FIELDS (SUBJECT)])')[1]
    subjects = [subjects[i] for i in range(0,len(subjects),2)]
    result = []
    for e in subjects:
        uid = str(e[0].split()[0],'utf8')
        subject = str(e[1].split()[1],'utf8')
        result.append((subject, uid))
    result = list(sorted(result))
    dup = [result[i][1] for i in range(1, len(result)) if result[i][0] == result[i-1][0]]
    imap.store(','.join(dup), '+FLAGS', '\\Seen')

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
    result = stream.readobject()
    if result == 'data':
        length = range[1] - range[0]
        with open(path, 'wb') as f:
            assert copy(stream, f, length) == length
    elif result == 'missing':
        missing = stream.readobject()
        raise Exception('missing: ' + ' '.join([str(e) for e in missing]))

if __name__ == '__main__':
    main()