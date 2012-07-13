from stream import copy, objectstream
from summary import generatesummary
from netserver import netserver
from timetuple import nowtuple
from autotemp import tempdir
import repo
from diskqueue import diskqueue
from filelock import filelock
import hashlib, pchex, threading, summary
import pickle, time, smtp, os, io, sys

usage = """\
server root key
"""

def run(root, key):
    print(usage)
    smtp = smtpserver(root)
    queue = smtp.getqueue()
    server(repo(root, key, queue)).start()
    smtp.run()

class smtpserver:
    def __init__(self, root):
        self._queue = diskqueue(os.path.join(root, 'sendqueue'))
    
    def getqueue(self):
        return self._queue
    
    def run(self):
        q = self._queue
        while True:
            if not q.empty():
                each = q.front()
                path = each[0]
                name = os.path.basename(path)
                with filelock(path):
                    with open(path, 'rb') as f:
                        data = f.read()
                hash = pchex.encode(hashlib.new('md5', data).digest())
                sender = 'histo@caipeichao.com'
                receiver = each[1]
                subject = name
                content = hash
                attachmentname = name
                attachmentdata = data
                smtp.sendmail(sender, receiver, subject, content, attachmentname, attachmentdata)
                q.pop()
            time.sleep(1)

class server(netserver):
    def __init__(self, repo):
        netserver.__init__(self, ('0.0.0.0', 13750), self.handle)
        self._commit = commit(repo)
        self._search = search(repo)
        self._get = get(repo)
        self._lock = threading.Lock()
    
    def handle(self, stream):
        method = stream.readobject()
        t = {'commit': self._commit.run,
             'search': self._search.run,
             'get': self._get.run}
        with self._lock:
            t[method](stream)

class commit:
    def __init__(self, repo):
        self._repo = repo
        
    def run(self, stream):
        datetime = stream.readobject()
        if datetime == None:
            datetime = nowtuple()
        name = stream.readobject()
        lastmodify = stream.readobject()
        filename = stream.readobject()
        filesize = stream.readobject()
        with tempdir('histo-repo-') as t:
            temp = os.path.join(t, filename)
            with open(temp, 'wb') as f:
                copy(stream, f, filesize)
            datafile = self._repo.open('data', 'wb')
            start = datafile.tell()
            with open(temp, 'rb') as f:
                copy(f, datafile, filesize)
            end = datafile.tell()
            summary = generatesummary(name, temp)
            index = (('datetime', datetime),
                     ('name', name),
                     ('last-modify', lastmodify),
                     ('range', (start, end)),
                     ('summary', summary))
            indexfile = self._repo.open('index', 'wb')
            objectstream(indexfile).writeobject(index)
            datafile.close()
            indexfile.close()
        stream.writeobject('ok')

class search:
    def __init__(self, repo):
        self._repo = repo
    
    def run(self, stream):
        index = []
        f = self._repo.open('index', 'rb')
        data = f.read()
        f.close()
        datalen = len(data)
        data = io.BytesIO(data)
        while data.tell() < datalen:
            item = pickle.load(data)
            index.append(dict(item))
        keyword = stream.readobject()
        result = []
        for e in index:
            for e2 in summary.walk(index['summary']):
                if e2.find(keyword) >= 0:
                    result.append(e)
                    break
        stream.writeobject(result)

class get:
    def __init__(self, repo):
        self._repo = repo
    
    def run(self, stream):
        range = stream.readobject()
        f = self._repo.open('data', 'rb')
        f.seek(range[0])
        copy(f, stream, range[1] - range[0])
        f.close()

if __name__ == '__main__':
    run(sys.argv[1], pchex.decode(sys.argv[2]))