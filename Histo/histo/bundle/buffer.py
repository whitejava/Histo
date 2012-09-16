class Buffer:
    def __init__(self, fastBundle, slowBundle, queueFile, usageLogFile, maxBufferSize, threadCount):
        self.fastBundle = fastBundle
        self.slowBundle = slowBundle
        self.queueFile = queueFile
        self.usageLogFile = usageLogFile
        self.maxBufferSize = maxBufferSize
        self.threadCount = threadCount
        self.queue = self.getQueue(queueFile)
        self.usageLog = self.getUsageLog(usageLogFile)
        self.threads = self.createTransferThreads(threadCount)
        self.startAllThreads(self.threads)
    
    def open(self, name, mode):
        if mode == 'wb':
            return self.openForWrite(name)
        elif mode == 'rb':
            return self.openForRead(name)
        else:
            raise Exception('No such mode.')
    
    def list(self):
        return self.slowBundle.list()
    
    def delete(self, name):
        raise Exception('Not support.')
    
    def getQueue(self, queueFile):
        return TaskQueue(queueFile)
    
    def getUsageLog(self, usageLogFile):
        return UsageLog(usageLogFile)
    
    def createTransferThreads(self, threadCount):
        return [self.createTransferThread() for _ in range(threadCount)]
    
    def startAllThreads(self, threads):
        for e in threads:
            e.start()
    
    def openForWrite(self, name):
        result = self.fastBundle.open(name, 'wb')
        close0 = result.close
        def close2():
            close0()
            self.limitBufferSize()
            self.addQueue(name)
        result.close = close2
        return result
    
    def openForRead(self, name):
        if not self.fastBundle.exists(name):
            self.transferSlowBundleToFastBundle(name)
        return self.fastBundle.open(name)
    
    def createTransferThread(self):
        return TransferThread(self.fastBundle, self.slowBundle, self.queue)
    
    def limitBufferSize(self):
        currentBufferSize = self.getCurrentBufferSize()
        mostUseless = self.getMostUseless()
        for e in mostUseless:
            try:
                self.fastBundle.delete(e)
                currentBufferSize -= self.fastBundle.getSize(e)
                if currentBufferSize <= self.maxBufferSize:
                    break
            except:
                pass

    def addQueue(self, name):
        self.queue.append(name)
    
    def transferSlowBundleToFastBundle(self, name):
        with self.slowBundle.open(name, 'rb') as f1:
            with self.fastBundle.open(name, 'wb') as f2:
                from pclib import copystream
                copystream(f1, f2)
                
    def getCurrentBufferSize(self):
        return sum(map(self.fastBundle.getSize, self.fastBundle.list()))
    
    def getMostUseless(self):
        files = self.fastBundle.list()
        files = [(-self.usageLog.getUsageCount(e), e) for e in files]
        files = sorted(files)
        files = [e[1] for e in files]
        return files

class TaskQueue:
    def __init__(self, file):
        self.file = file
        self.queue = self.loadOrCreate(file)
        from threading import Semaphore, Lock
        self.semaphore = Semaphore(0)
        self.lock = Lock()
        Stuck
    
    def append(self, x):
        with self.lock:
            self.queue.append((x, False))
            self.semaphore.release()
    
    def fetch(self):
        self.semaphore.acquire()
        with self.lock:
            for i,e,f in self.queue:
                if not f:
                    return e
                Stuck
    
    def feedBack(self, fetchId, result):
        pass
    
    def loadOrCreate(self, file):
        pass

class UsageLog:
    def __init__(self, file):
        self.file = file
        self.usage = self.loadOrCreate(file)
    
    def log(self, name):
        self.logToMemory(name)
        self.logToFile(name)
    
    def getUsageCount(self, name):
        return self.usage[name]
    
    def loadOrCreate(self, file):
        import os
        if os.path.exists(file):
            return self.loadUsage()
        else:
            self.createUsageDirectory(file)
            return self.createUsage()
    
    def logToMemory(self, name):
        self.usage[name] += 1
    
    def logToFile(self, name):
        with open(name, 'a', encoding = 'utf8') as f:
            from pclib import timetext
            print('%s %s' % (timetext(), repr(name)), file=f)
    
    def loadUsage(self):
        usage = self.createUsage()
        with open(self.file, 'r', encoding = 'utf8') as f:
            for e in f:
                e = e[:-1]
                time, name = e.split(' ', 1)
                name = eval(name)
                usage[name] += 1
        return usage
    
    def createUsageDirectory(self, file):
        import os
        directory = os.path.dirname(file)
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def createUsage(self):
        from collections import defaultdict
        return defaultdict(0)

from threading import Thread
class TransferThread(Thread):
    def __init__(self, fastBundle, slowBundle, queue):
        Thread.__init__(self)
        self.fastBundle = fastBundle
        self.slowBundle = slowBundle
        self.queue = queue
    
    def run(self):
        while True:
            fetchId, task = self.queue.fetch()
            result = self.runTask(task)
            self.queue.feedBack(fetchId, result)
    
    def runTask(self, task):
        try:
            self.runTask2(task)
            return True
        except:
            return False
        
    def runTask2(self, task):
        with self.fastBundle.open(task, 'rb') as f1:
            with self.slowBundle.open(task, 'wb') as f2:
                from pclib import copystream
                copystream(f1, f2)

class buffer:
    def __init__(self, fast, slow, queuefile, usagelogfile, buffersize, threadcount):
        self.fast = fast
        self.slow = slow
        self.usagelog = usagelog(usagelogfile)
        self.buffersize = buffersize
        queue = taskqueue(diskqueue(queuefile))
        self.queue = queue
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
            if e not in self.queue:
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
    
    def list(self):
        return self.slow.list()

class transferthread(threading.Thread):
    def __init__(self, fast, slow, queue):
        threading.Thread.__init__(self)
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
