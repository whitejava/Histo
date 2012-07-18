from stream import copy, objectstream
from summary import generatesummary
from netserver import netserver
from timetuple import nowtuple, totuple
from autotemp import tempdir
from repo import repo
from datetime import datetime
from taskqueue import diskqueue,taskqueue, NoTask
from filelock import filelock
from threading import Thread
import hashlib, pchex, threading, summary
import time, smtp, os, io, sys, logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='[%Y-%m%d %H:%M:%S]')

usage = """\
server root key
"""

def run(root, key):
    print(usage)
    smtp = smtpserver(root)
    queue = smtp.getqueue()
    logging.debug('Starting main server')
    main = mainserver(repo(root, key, queue))
    main.start()
    logging.debug('Starting smtp service')
    smtp.start()
    logging.debug('Service running')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    smtp.shutdown()
    main.shutdown()

class sendthread(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self._queue = queue
        self._exit = False
    
    def shutdown(self):
        self._exit = True
    
    def run(self):
        while not self._exit:
            time.sleep(1)
            try:
                taskid, each = self._queue.fetchtask()
            except NoTask:
                continue
            path = each[0]
            name = os.path.basename(path)
            with filelock(path):
                lastmodify = os.path.getmtime(path)
                filesize = os.path.getsize(path)
                with open(path, 'rb') as f:
                    data = f.read()
            lastmodify = datetime.fromtimestamp(lastmodify)
            lastmodify = totuple(lastmodify)
            lastmodify = '{:04d}-{:02d}{:02d}-{:02d}{:02d}{:02d}-{:06d}'.format(*lastmodify)
            hash = pchex.encode(hashlib.new('md5', data).digest())
            sender = 'histo@caipeichao.com'
            receiver = each[1]
            subject = name
            content = '%s-%s-%s' % (filesize, lastmodify, hash)
            attachmentname = name
            attachmentdata = data
            logging.debug('sending {} to {}'.format(name, receiver))
            try:
                smtp.sendmail(sender, receiver, subject, content, attachmentname, attachmentdata)
            except Exception as e:
                logging.debug('fail send %s' % name)
                self._queue.feedback(taskid, False)
                logging.exception(e)
            else:
                self._queue.feedback(taskid, True)
            logging.debug('finish send {}'.format(name))

class smtpserver:
    def __init__(self, root):
        self._queue = taskqueue(diskqueue(os.path.join(root, 'sendqueue')))
    
    def getqueue(self):
        return self._queue
    
    def shutdown(self):
        for e in self._threads:
            e.shutdown()
    
    def start(self):
        threadcount = 5
        self._threads = [sendthread(self._queue) for i in range(threadcount)]
        for e in self._threads:
            e.start()

def loadindex(repo):
    try:
        f = repo.open('index', 'rb')
    except IOError:
        return []
    missing = f.getmissingparts()
    if missing:
        raise Exception('Missing parts: ' + ' '.join([str(e) for e in missing]))
    stream = f.read()
    f.close()
    stream = objectstream(io.BytesIO(stream))
    result = []
    while True:
        try:
            result.append(indexitem(stream.readobject()))
        except EOFError:
            break
    return result

def indexitem(x):
    return dict(x)

class mainserver(netserver):
    def __init__(self, repo):
        netserver.__init__(self, ('127.0.0.1', 13750), self.handle)
        self._index = loadindex(repo)
        self._commit = commit(repo, self._index)
        self._localcommit = localcommit(repo, self._index)
        self._search = search(self._index)
        self._get = get(repo)
        self._upload = upload(repo)
        self._lock = threading.Lock()
    
    def handle(self, stream):
        method = stream.readobject()
        logging.debug('request: ' + method)
        t = {'commit': self._commit.run,
             'localcommit': self._localcommit.run,
             'search': self._search.run,
             'get': self._get.run,
             'upload': self._upload.run}
        with self._lock: #WARNING: Careful remove the lock. Thinking about multithread situation
            t[method](stream)

class commit:
    def __init__(self, repo, index):
        self._repo = repo
        self._index = index
        
    def run(self, stream):
        datetime = stream.readobject()
        name = stream.readobject()
        lastmodify = stream.readobject()
        filename = stream.readobject()
        filesize = stream.readobject()
        logging.debug('name: ' + name)
        logging.debug('filesize: {}'.format(filesize))
        logging.debug('receiving data')
        with tempdir('histo-repo-') as t:
            temp = os.path.join(t, filename)
            with open(temp, 'wb') as f:
                assert copy(stream, f, filesize) == filesize
            logging.debug('receive data ok')
            logging.debug('writting to repo')
            localcommit(self._repo, self._index).commit(datetime, name, lastmodify, temp)
            logging.debug('write ok')
        stream.writeobject('ok')
        logging.debug('all ok')

class localcommit:
    def __init__(self, repo, index):
        self._repo = repo
        self._index = index
    
    def run(self, stream):
        time = stream.readobject()
        if time == None:
            time = nowtuple()
        name = stream.readobject()
        filename = stream.reaobject()
        lastmodify = os.path.getmtime(filename)
        logging.debug('localcommit:', filename)
        logging.debug('writing to repo')
        self.commit(time, name, lastmodify, filename)
        logging.debug('write ok')
        stream.writeobject('ok')
        logging.debug('all ok')
    
    def commit(self, datetime, name, lastmodify, filename):
        repo = self._repo
        datafile = repo.open('data', 'wb')
        start = datafile.tell()
        with open(filename, 'rb') as f:
            copy(f, datafile)
        end = datafile.tell()
        summary = generatesummary(name, filename, depthlimit = 2)
        index = (('datetime', datetime),
                 ('name', name),
                 ('last-modify', lastmodify),
                 ('range', (start, end)),
                 ('summary', summary))
        indexfile = repo.open('index', 'wb')
        objectstream(indexfile).writeobject(index)
        datafile.close()
        indexfile.close()
        self._index.append(index)

class search:
    def __init__(self, index):
        self._index = index
    
    def run(self, stream):
        keyword = stream.readobject()
        result = []
        for e in self._index:
            for e2 in summary.walk(e['summary']):
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
        missing = f.getmissingparts(range[0], range[1])
        if missing:
            stream.writeobject('missing')
            stream.writeobject(missing)
        else:
            stream.writeobject('data')
            f.seek(range[0])
            copy(f, stream, range[1] - range[0])
        f.close()

class upload:
    def __init__(self, repo):
        self._repo = repo
    
    def run(self, stream):
        type = stream.readobject()
        filename = stream.readobject()
        data = stream.readobject()
        try:
            self._repo.add_raw(type, filename, data)
        except ValueError as e:
            if e.args[0] == 'file existed':
                stream.writeobject('fail')
        else:
            stream.writeobject('ok')

if __name__ == '__main__':
    run(sys.argv[1], pchex.decode(sys.argv[2]))