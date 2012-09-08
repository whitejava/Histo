import os, smtp, time, io, pclib, threading
from pclib import filelock
from pclib import copystream
from taskqueue import taskqueue, diskqueue

class local:
    def __init__(self, root, idformat):
        if not os.path.exists(root): os.makedirs(root)
        self._root = root
        self._idformat = idformat
    
    def dump(self, n, data):
        path = self.getpath(n)
        with filelock(path):
            with open(path, 'wb') as f:
                f.write(data)
    
    def load(self, n):
        path = self.getpath(n)
        with filelock(path):
            with open(path, 'rb') as f:
                return f.read()
    
    def exists(self, n):
        path = self.getpath(n)
        return os.path.isfile(path)
    
    def getpath(self, n):
        n = self._idformat.format(n)
        path = os.path.join(self._root, n)
        return path

class local2:
    def __init__(self, root):
        if not os.path.exists(root):
            os.makedirs(root)
        self.root = root
    
    def open(self, name, mode):
        return open(os.path.join(self.root, name), mode)
    
    def list(self):
        return os.listdir(self.root)

class limit:
    def __init__(self, bundle, writespeed, readspeed):
        self.bundle = bundle
        self.writespeed = writespeed
        self.readspeed = readspeed
    
    def open(self, name, mode):
        f = self.bundle.open(name, mode)
        if mode == 'rb':
            return limitreader(f, self.readspeed)
        elif mode == 'wb':
            return limitwriter(f, self.writespeed)
        else:
            raise Exception('Mode error.')

def speedlimit(speed, totalbytes, minsleep = 0.01, maxsleep = 0.1):
    starttime = time.clock()
    yieldbytes = 0
    while yieldbytes < totalbytes:
        remainbytes = totalbytes - yieldbytes
        sleep = remainbytes / speed
        if sleep > maxsleep:
            sleep = maxsleep
        if sleep < minsleep:
            sleep = minsleep
        time.sleep(sleep)
        steptime = time.clock()
        elapsedtime = steptime - starttime
        expectyieldbytes = int(elapsedtime * speed)
        stepbytes = expectyieldbytes - yieldbytes
        if stepbytes > remainbytes:
            stepbytes = remainbytes
        if stepbytes > 0:
            yield stepbytes
        yieldbytes += stepbytes

def test_speedlimit():
    for e in speedlimit(10*1024, 1024*1024):
        print(e)

class limitreader:
    def __init__(self, file, speed):
        self.file = file
        self.speed = speed
        
    def read(self, limit):
        result = bytearray()        
        for e in speedlimit(self.speed, limit):
            read = self.file.read(limit)
            if not read:
                break
            result.extend(read)
        return result

class limitwriter:
    def __init__(self, file, speed):
        self.file = file
        self.speed = speed
    
    def write(self, data):
        io = io.BytesIO(data)
        for e in speedlimit(self.speed, len(data)):
            x = io.read(e)
            assert len(x) is e
            self.file.write(x)

class crypto:
    def __init__(self, bundle, cipher):
        self._bundle = bundle
        self._cipher = cipher
    
    def dump(self, n, data):
        data = self._cipher.encode(data)
        self._bundle.dump(n, data)
    
    def load(self, n):
        data = self._bundle.load(n)
        data = self._cipher.decode(data)
        return data
    
    def exists(self, n):
        return self._bundle.exists(n)

class listen:
    def __init__(self, bundle, listener):
        self._bundle = bundle
        self._listener = listener
    
    def dump(self, n, data):
        self._bundle.dump(n, data)
        self._listener(n)
    
    def load(self, n):
        return self._bundle.load(n)
    
    def exists(self, n):
        return self._bundle.exists(n)

class mail:
    def __init__(self, sender, mail, password):
        self._sender = sender
        self._mail = mail
        self._password = password
    
    def dump(self, n, data, stopper = [False]):
        sender = self._sender
        receiver = self._mail
        subject = str(n)
        content = ''
        attachmentname = str(n)
        attachmentdata = data
        smtp.sendmail(sender, receiver, subject, content, attachmentname, attachmentdata, stopper)
    
    def load(self, n):
        raise Exception('not impl')
    
    def delete(self, n):
        raise Exception('not impl')

class bufferedbundle:
    def __init__(self, quick, slow, queuefile, usagelogfile, buffersize, threadcount):
        self.usagelogfile = usagelogfile
        self.buffersize = buffersize
        self.quick = quick
        self.slow = slow
        self.queuefile = queuefile
        self.usage = dict()
        self.queue = taskqueue(diskqueue(queuefile))
        self.queuelock = threading.Lock()
        self.threads = []
        for _ in threadcount:
            self.threads.append(self.transferthread(self))
        if os.path.exists(queuefile):
            with open(queuefile, encode='utf8') as f:
                for e in f:
                    self.queue.append(eval(e[:-1]))
        else:
            d = os.path.dirname(queuefile)
            if not os.path.exists(d):
                os.makedirs(d)
        if os.path.exists(usagelogfile):
            with open(usagelogfile, encode='utf8') as f:
                for e in f:
                    e = eval(e[:-1])
                    self.addusage(e)
        else:
            d = os.path.dirname(usagelogfile)
            if not os.path.exists(d):
                os.makedirs(d)
    
    def open(self, name, mode):
        if mode == 'rb':
            return self.readfile(name)
        elif mode == 'wb':
            return self.writefile(name)
        else:
            raise Exception('No such mode')
        
    def readfile(self, name):
        if self.quick.exists(name):
            return self.quick.open(name, 'rb')
        elif self.slow.exists(name):
            self.transferslowfileintoquickbundle(name)
            return self.quick.open(name, 'rb')
        else:
            raise Exception('File not found')
    
    def transferslowfileintoquickbundle(self, name):
        size = self.slow.getsize(name)
        self.requestspace(size)
        with self.slow.open(name, 'rb') as f1:
            with self.quick.open(name, 'wb') as f2:
                copiedsize = copystream(f1, f2)
                assert copiedsize is size
    
    def writefile(self, name):
        def onclose(close0, *k, **kw):
            close0(*k, **kw)
            self.requestspace(self.quick.getsize(name))
            self.addtransfertask(name)
        result = self.quick.open(name, 'wb')
        result.close = pclib.hook(result.close, onclose)
        return result
    
    def requestspace(self, space):
        targetsize = self.buffersize - space
        if targetsize < 0:
            targetsize = 0
        files = self.quick.list()
        totalsize = 0
        for e in files:
            totalsize += self.quick.getsize(e)
        useless = self.getmostuseless()
        while totalsize > targetsize:
            if len(useless) is 0:
                return False
            deleting = useless[0]
            if not self.inuse(deleting):
                totalsize -= self.quick.getsize(deleting)
                self.quick.delete(deleting)
            del useless[0]
        return True
    
    def addtransfertask(self, name):
        self.queue.append(name)
    
    def addusage(self, name):
        if name in self.usage:
            self.usage[name] += 1
        else:
            self.usage[name] = 1
    
    class transferthread(threading.Thread):
        def __init__(self, quick, slow, queue):
            threading.Thread.__init__(self)
            self.quick = quick
            self.slow = slow
            self.queue = queue
            
        def run(self):
            while True:
                fetchid, task = self.queue.fetchtask()
                try:
                    with self.quick.open(task, 'rb') as f:
                        with self.slow.open(task, 'wb') as f2:
                            copystream(f, f2)
                except BaseException:
                    self.queue.feedback(fetchid, False)
                else:
                    self.queue.feedback(fetchid, True)

if __name__ == '__main__':
    test_speedlimit()