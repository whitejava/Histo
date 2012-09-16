import os, smtp, time, io, pclib, threading
from taskqueue import taskqueue, diskqueue
import random

class fileisinuse(Exception):
    pass

def addcontextmanager(x):
    x.__enter__ = lambda self: self
    x.__exit__ = lambda self,*k: x.close(self)
    return x

def safedelete(x):
    inuse = []
    open0 = x.open
    delete0 = x.delete
    def myopen(name, mode):
        inuse.append(name)
        try:
            result = open0(name, mode)
        except Exception:
            inuse.remove(name)
        else:
            close0 = result.close
            def myclose():
                try:
                    close0()
                finally:
                    inuse.remove(name)
            result.close = myclose
            return result
    def mydelete(name):
        if name in inuse:
            raise fileisinuse()
        delete0(name)
    x.open = myopen
    x.delete = mydelete
    return x

@safedelete
class local:
    def __init__(self, root):
        if not os.path.exists(root):
            os.makedirs(root)
        self.root = root
    
    def open(self, name, mode):
        return open(os.path.join(self.root, name), mode)
    
    def list(self):
        return os.listdir(self.root)
    
    def delete(self, name):
        os.unlink(name)

class speedlimit:
    def __init__(self, speed, minsleep = 0.01, maxsleep = 0.1):
        self.speed = speed
        self.minsleep = minsleep
        self.maxsleep = maxsleep
        self.starttime = time.clock()
        self.yieldbytes = 0
        self.totalbytes = 0
    
    def fetch(self, fetchbytes):
        self.totalbytes += fetchbytes
        while self.yieldbytes < self.totalbytes:
            remainbytes = self.totalbytes - self.yieldbytes
            sleep = remainbytes / self.speed
            sleep = pclib.limitrange(sleep, self.minsleep, self.maxsleep)
            time.sleep(sleep)
            steptime = time.clock()
            elapsedtime = steptime - self.starttime
            expectyieldbytes = int(elapsedtime * self.speed)
            stepbytes = expectyieldbytes - self.yieldbytes
            if stepbytes > remainbytes:
                stepbytes = remainbytes
            if stepbytes > 0:
                yield stepbytes
            self.yieldbytes += stepbytes

def test_speedlimit():
    s = speedlimit(10*1024)
    for i in reversed([2**e for e in range(16)]):
        print('start %d' % i)
        for e in s.fetch(i):
            print(e)

@safedelete
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
        
    def delete(self, name):
        self.bundle.delete(name)

def test_limit():
    a = local('D:\\%s-test-limit' % pclib.timetext())
    a = limit(a, 1024*1024, 4*1024*1024)
    data = bytes([1]*1024)
    with pclib.timer():
        with a.open('a', 'wb') as f:
            for _ in range(8):
                f.write(data*512)
    with pclib.timer():
        with a.open('a', 'rb') as f:
            while True:
                if f.read(1024*512) is None:
                    break

@addcontextmanager
class limitreader:
    def __init__(self, file, speed):
        self.file = file
        self.limiter = speedlimit(speed)
        
    def read(self, limit):
        result = bytearray()
        for e in self.limiter.fetch(limit):
            read = self.file.read(e)
            if not read:
                break
            result.extend(read)
        if not result:
            return None
        return result
    
    def close(self):
        self.file.close()

@addcontextmanager
class limitwriter:
    def __init__(self, file, speed):
        self.file = file
        self.limiter = speedlimit(speed)
    
    def write(self, data):
        stream = io.BytesIO(data)
        for e in self.limiter.fetch(len(data)):
            x = stream.read(e)
            assert len(x) == e
            self.file.write(x)
            
    def close(self):
        self.file.close()

class usagelog:
    def __init__(self, file):
        self.file = file
        if os.path.exists(file):
            self.usage = self.loadlog(file)
        else:
            os.makedirs(os.path.dirname(file))
            self.usage = dict()
        
    def log(self, name):
        self.statisticusage(name)
        self.logtofile(name)
    
    def logtofile(self, name):
        with open(self.file, 'w') as f:
            time = '%04d%02d%02d%02d%02d%02d%06d' % pclib.nowtuple()
            print('%s %s'%(time, repr(name)), file=f)
    
    def loadlog(self, file):
        with open(self.file, 'r') as f:
            for e in f:
                e = e[:-1]
                time, name = e.split(' ', 1)
                name = eval(name)
                self.statisticusage(name)
    
    def statiticusage(self, name):
        if name in self.usage:
            self.usage[name] += 1
        else:
            self.usage[name] = 1
            
    def getusagecount(self, name):
        if name in self.usage:
            return self.usage[name]
        return 0

@safedelete
class buffer:
    def __init__(self, fast, slow, queuefile, usagelogfile, buffersize, threadcount):
        self.fast = fast
        self.slow = slow
        self.usagelog = usagelog(usagelogfile)
        self.buffersize = buffersize
        queue = taskqueue(diskqueue(queuefile))
        self.threads = [transferthread(fast, slow, queue) for _ in range(threadcount)]
        for e in self.threads:
            e.start()
    
    def open(self, name, mode):
        self.usagelog.log(name)
        if mode == 'rb':
            return self.openforread(name)
        elif mode == 'wb':
            return self.openforwrite(name)
        else:
            raise Exception('No such mode.')
    
    def delete(self, name):
        raise Exception('Not support')
    
    def openforread(self, name):
        if self.fast.exists(name):
            return self.fast.open(name, 'rb')
        elif self.slow.exists(name):
            self.transferslowtofast(name)
        else:
            raise Exception('File not exist.')
    
    def openforwrite(self, name):
        result = self.fast.open(name, 'wb')
        result.close = lambda: result.close(); self.limitbuffersize()
        return result
    
    def transferslowtofast(self, name):
        with self.slow.open(name, 'rb') as f1:
            with self.fast.open(name, 'wb') as f2:
                assert pclib.copystream(f1, f2) == self.slow.getsize(name)
    
    def limitbuffersize(self):
        currentbuffersize = self.getcurrentbuffersize()
        mostuseless = self.getmostuselessfastfiles()
        for e in mostuseless:
            if currentbuffersize <= self.buffersize:
                break
            size = self.fast.getsize(e)
            try:
                self.fast.delete(e)
            except Exception:
                continue
            else:
                self.currentbuffersize -= size
    
    def getcurrentbuffersize(self):
        result = 0
        for e in self.fast.list():
            result += self.fast.getsize(e)
        return result
    
    def getmostuselessfastfiles(self):
        files = self.fast.list()
        files = [(-self.usagelog.getusagecount(e), e) for e in files]
        files = sorted(files)
        files = [e[1] for e in files]
        return files

class transferthread(threading.Thread):
    def __init__(self, fast, slow, queue):
        self.fast = fast
        self.slow = slow
        self.queue = queue
    
    def run(self):
        while True:
            fetchid, task = self.queue.fetchtask()
            result = self.runtask(task)
            self.queue.feedback(fetchid, result)
    
    def runtask(self, task):
        try:
            self.runtask2(task)
        except Exception:
            return False
        else:
            return True

    def runtask2(self, task):
        with self.slow.open(task, 'wb') as f1:
            with self.fast.open(task, 'rb') as f2:
                assert pclib.copystream(f2, f1) == self.fast.getsize(task)

def test_buffer():
    pass

if __name__ == '__main__':
    #test_speedlimit()
    test_limit()