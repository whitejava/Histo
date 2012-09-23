__all__ = ['Buffer']

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
        self.queue = DiskQueue(file)
        self.fetched = []
        from threading import Lock, Semaphore
        self.semaphore = Semaphore(len(self.queue))
        self.lock = Lock()
    
    def append(self, x):
        with self.lock:
            self.queue.append(self.Task(x))
            self.semaphore.release()
        
    def fetch(self):
        self.semaphore.acquire()
        with self.lock:
            task = self.findUnfetch()
            self.fetched.append(task)
            return task, task.value
    
    def feedBack(self, fetchId, result):
        with self.lock:
            self.fetched.remove(fetchId)
            if result:
                self.queue.remove(fetchId)
            else:
                self.semaphore.release()
    
    class Task:
        def __init__(self, value):
            self.value = value
            
    def findUnfetch(self):
        for e in self.queue:
            if not self.isFetched(e):
                return e
        raise Exception('Not found.')
    
    def isFetched(self, task):
        for e in self.fetched:
            if e.value is task:
                return True
        return False

class DiskQueue:
    def __init__(self, file):
        self.file = file
        self.queue = self.loadOrCreate()
    
    def append(self, x):
        self.queue.append(x)
        self.save()
    
    def remove(self, x):
        self.queue.remove(x)
        self.save()
    
    def __getitem__(self, key):
        return self.queue[key]
    
    def __setitem__(self, key, value):
        self.queue[key] = value
        self.save()
        
    def __iter__(self):
        return self.queue.__iter__()
    
    def save(self):
        with open(self.file, 'w') as f:
            for e in self.queue:
                print(repr(e), file=f)
    
    def loadOrCreate(self):
        import os
        if os.path.exists(self.file):
            return self.loadQueue()
        else:
            return []
    
    def loadQueue(self):
        result = []
        with open(self.file, 'r') as f:
            for e in f:
                result.append(eval(e))
        return result

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
