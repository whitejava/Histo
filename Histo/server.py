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
import hashlib, pchex, threading, summary, tempfile
import time, smtp, os, io, sys, logging, shutil
import autotemp, subprocess

logpath = 'E:\\histo-log\\0.log'
logdateformat = '[%Y-%m%d %H:%M:%S]'

#Log to file
logging.basicConfig(filename=logpath,
                    level=logging.DEBUG,
                    format='%(levelname)s - %(asctime)s %(message)s',
                    datefmt=logdateformat)

#Display log on console
formatter = logging.Formatter('%(asctime)s %(message)s')
formatter.datefmt = logdateformat
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

# Usage:
# server root key threadcount

def main(root, key, threadcount = '5'):
    key = pchex.decode(key)
    threadcount = int(threadcount)
    
    logging.debug('Loading smtp server')
    smtp = smtpserver(root, threadcount)
    queue = smtp.getqueue()
    
    logging.debug('Loading main server')
    main = mainserver(repo(root, key, queue))
    
    logging.debug('Starting main server')
    main.start()
    
    logging.debug('Starting smtp service')
    smtp.start()
    
    logging.debug('Service running')
    wait_for_keyboard_interrupt()
    
    logging.debug('Service shutting down')
    smtp.shutdown()
    main.shutdown()
    
    logging.debug('Now exit')

def wait_for_keyboard_interrupt():
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        return

class sendthread(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self._queue = queue
        self._stopper = [False]
        self._exitlock = threading.Lock()
        self._exitlock.acquire()
    
    def shutdown(self):
        self._stopper[0] = True
    
    def wait(self):
        self._exitlock.acquire()
        self._exitlock.release()
    
    def run(self):
        try:
            while not self._stopper[0]:
                time.sleep(1)
                try:
                    taskid, each = self._queue.fetchtask()
                except NoTask:
                    continue
                path = each[0]
                receiver = each[1]
                name = os.path.basename(path)
                logging.debug('fetch ' + name)
                with filelock(path):
                    lastmodify = os.path.getmtime(path)
                    filesize = os.path.getsize(path)
                    with open(path, 'rb') as f:
                        data = f.read()
                    assert len(data) == filesize
                lastmodify = datetime.fromtimestamp(lastmodify)
                lastmodify = totuple(lastmodify)
                lastmodify = '{:04d}-{:02d}{:02d}-{:02d}{:02d}{:02d}-{:06d}'.format(*lastmodify)
                md5 = pchex.encode(hashlib.new('md5', data).digest())
                sender = 'histo@caipeichao.com'
                subject = name
                content = '%s-%s-%s' % (filesize, lastmodify, md5)
                attachmentname = name
                attachmentdata = data
                logging.debug('sending {} to {}'.format(name, receiver))
                try:
                    smtp.sendmail(sender, receiver, subject, content, attachmentname, attachmentdata, stopper = self._stopper)
                except Exception as e:
                    logging.warning('fail send %s' % name)
                    self._queue.feedback(taskid, False)
                else:
                    self._queue.feedback(taskid, True)
                    logging.debug('finish send {}'.format(name))
        except Exception as e:
            logging.exception(e)
        finally:
            self._exitlock.release()

class smtpserver:
    def __init__(self, root, threadcount = 5):
        self._threadcount = threadcount
        self._queue = taskqueue(diskqueue(os.path.join(root, 'sendqueue')))
    
    def getqueue(self):
        return self._queue
    
    def start(self):
        self._threads = [sendthread(self._queue) for i in range(self._threadcount)]
        for e in self._threads:
            e.start()
    
    def shutdown(self):
        for e in self._threads:
            e.shutdown()
        for e in self._threads:
            e.wait()

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
        self._lock = threading.Lock()
    
    def handle(self, stream):
        method = stream.readobject()
        logging.debug('request: ' + method)
        t = {'remotecommit': self._remotecommit,
             'localcommit': self._localcommit,
             'search': self._search,
             'get': self._get,
             'commitunpack': self._commitunpack,
             'upload': self._upload}
        with self._lock: #WARNING: Careful remove the lock. Thinking about multithread situation
            try:
                t[method](stream)
            except Exception as e:
                logging.exception(e)

    def _remotecommit(self, stream):
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
            self._commitpack(datetime, name, lastmodify, temp)
            logging.debug('write ok')
        stream.writeobject('ok')
        logging.debug('all ok')

    def _localcommit(self, stream):
        time = stream.readobject()
        if time == None:
            time = nowtuple()
        name = stream.readobject()
        filename = stream.readobject()
        lastmodify = os.path.getmtime(filename)
        logging.debug('localcommit: ' + filename)
        logging.debug('writing to repo')
        self._commitpack(time, name, lastmodify, filename)
        logging.debug('write ok')
        stream.writeobject('ok')
        logging.debug('all ok')
    
    def _commitpack(self, datetime, name, lastmodify, filename):
        repo = self._repo
        datafile = repo.open('data', 'wb')
        start = datafile.tell()
        with open(filename, 'rb') as f:
            copy(f, datafile)
        end = datafile.tell()
        logging.debug('generating summary')
        summary = generatesummary(name, filename, depthlimit = 2)
        index = (('datetime', datetime),
                 ('name', name),
                 ('last-modify', lastmodify),
                 ('range', (start, end)),
                 ('summary', summary))
        logging.debug('writing index')
        indexfile = repo.open('index', 'wb')
        objectstream(indexfile).writeobject(index)
        datafile.close()
        indexfile.close()
        self._index.append(indexitem(index))

    def _commitunpack(self, stream):
        path = stream.readobject()
        compress = stream.readobject()
        datetime = nowtuple()
        name = os.path.basename(path)
        lastmodify = os.path.getmtime(path)
        path2 = path + '-committing'
        shutil.move(path, path2)
        summary = generatesummary(name, path2, depthlimit = 2)
        archive = self._pack(compress, path2)
        datafile = self._repo.open('data', 'wb')
        start = datafile.tell()
        with open(archive, 'rb') as f:
            copy(f, datafile)
        end = datafile.tell()
        os.unlink(archive)
        index = (('datetime', datetime),
                 ('name', name),
                 ('last-modify', lastmodify),
                 ('range', (start, end)),
                 ('summary', summary))
        indexfile = repo.open('index', 'wb')
        objectstream(indexfile).writeobject(index)
        datafile.close()
        indexfile.close()
        self._index.append(indexitem(index))
        stream.writeobject('ok')
        
    def _pack(self, compress, directory):
        archiveroot = 'G:\\'
        
        #Generate current time
        time = datetime.now()
        time = time.timetuple()
        time = time[:6]
        time = '{:04d}-{:02d}-{:02d}-{:02d}-{:02d}-{:02d}'.format(*time)
    
        #Handle compression paramter
        t = {False:'-m0', True:'-m5'}
        compression = t[compress]
        
        #Get archive name
        name = os.path.basename(directory)
        
        #Get archive full path
        archive = '{}-{}.rar'.format(time, name)
        archive = os.path.join(archiveroot, archive)
        
        #Generate file list
        files = os.listdir(directory)
        if not files:
            files = ['Empty']
            with open(os.path.join(directory, 'Empty'),'wb'): pass
        files = '\n'.join(files) + '\n'
        files = bytes(files, 'utf16')
        
        #Create listfile
        listfile = tempfile.NamedTemporaryFile(mode = 'wb', delete = False)
        listfile.write(files)
        listfile.close()
        
        #Change working directory for rar
        os.chdir(directory)
        
        #Call rar to compress
        command = ['rar',
                   'a', #Create archive file
                   '"{}"'.format(archive), #Archive path
                   '@"{}"'.format(listfile.name), #List file
                   '-df', #Delete file after complete
                   '-scul', #List file is utf16
                   compression, #compression
                   '-w"{}"'.format(directory)] #Set working directory
        command = ' '.join(command)
        subprocess.call(command)
        
        #Restore working directory
        path = os.path.dirname(__file__)
        os.chdir(path)
        
        #Clean up
        os.remove(listfile.name)
        os.rmdir(directory)
        
        #Return
        return archive

    def _search(self, stream):
        keyword = stream.readobject()
        result = []
        for e in self._index:
            for e2 in summary.walk(e['summary']):
                if e2.find(keyword) >= 0:
                    result.append(e)
                    break
        stream.writeobject(result)

    def _get(self, stream):
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

    def _upload(self, stream):
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
    main(*sys.argv[1:])