__all__ = ['Buffer']

import logging
logger = logging.getLogger()

class Buffer:
    def __init__(self, fastBundle, slowBundle, queueFile, usageLogFile, maxBufferSize, threadCount):
        from histo.bundle import Safe
        self.fastBundle = Safe(fastBundle)
        self.slowBundle = slowBundle
        self.queueFile = queueFile
        self.usageLogFile = usageLogFile
        self.maxBufferSize = maxBufferSize
        self.threadCount = threadCount
        self.queue = self.getQueue(queueFile)
        self.usageLog = self.getUsageLog(usageLogFile)
        self.threads = self.createTransferThreads(threadCount)
        self.startAllThreads(self.threads)
        from threading import Lock
        self.lock = Lock()
    
    def open(self, name, mode):
        if mode == 'wb':
            return self.openForWrite(name)
        elif mode == 'rb':
            return self.openForRead(name)
        else:
            raise Exception('No such mode.')
    
    def list(self):
        logger.debug('List')
        result = set()
        result.union()
        slowFiles = self.slowBundle.list()
        fastFiles = self.fastBundle.list()
        logger.debug('Slow files: %d' % len(slowFiles))
        logger.debug('Fast files: %d' % len(fastFiles))
        result = result.union(slowFiles)
        result = result.union(fastFiles)
        result = list(result)
        logger.debug('Return Length %d' % len(result))
        return result
    
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
        logger.debug('Open wb %s' % name)
        result = self.fastBundle.open(name, 'wb')
        def preClose():
            logger.debug('Closing %s' % name)
            self.addQueue(name)
            self.limitBufferSize()
        def postClose():
            logger.debug('Finish Close %s' % name)
        return FileHook(result, preClose=preClose, postClose=postClose)
    
    def openForRead(self, name):
        logger.debug('Open rb %s' % name)
        if not self.fastBundle.exists(name):
            logger.debug('Out of cache')
            self.transferSlowBundleToFastBundle(name)
        return self.fastBundle.open(name, 'rb')
    
    def createTransferThread(self):
        return TransferThread(self.fastBundle, self.slowBundle, self.queue)
    
    def limitBufferSize(self):
        logger.debug('Limit buffer size')
        with self.lock:
            currentBufferSize = self.getCurrentBufferSize()
            mostUseless = self.getMostUseless()
            for e in mostUseless:
                if currentBufferSize <= self.maxBufferSize:
                    break
                if e in self.queue:
                    logger.debug('%s is in queue' % e)
                    continue
                logger.debug('Current buffer size %s' % currentBufferSize)
                fileSize = self.fastBundle.getSize(e)
                logger.debug('Delete %s' % e)
                from histo.bundle.safe import SafeProtection
                try:
                    self.fastBundle.delete(e)
                except SafeProtection as ex:
                    logger.debug('Delete not allowed %s' % e)
                except Exception as ex:
                    logger.debug('Delete error %s' % e)
                    logger.exception(ex)
                else:
                    logger.debug('Delete ok %s' % e)
                    currentBufferSize -= fileSize

    def addQueue(self, name):
        self.queue.append(name)
    
    def transferSlowBundleToFastBundle(self, name):
        logger.debug('Transfer slow to fast %s' % name)
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
        self.queue = self.DiskQueue(file)
        self.fetched = []
        from threading import Lock, Semaphore
        self.semaphore = Semaphore(len(self.queue))
        self.lock = Lock()
    
    def __iter__(self):
        return iter(self.queue)
    
    def append(self, x):
        with self.lock:
            logger.debug('Append %s' % x)
            self.queue.append(self.Task(x))
            self.semaphore.release()
        
    def fetch(self):
        self.semaphore.acquire()
        with self.lock:
            task = self.findUnfetch()
            logger.debug('Fetch %s %s' % (id(task), task.value))
            self.fetched.append(task)
            return task, task.value
    
    def feedBack(self, fetchId, result):
        with self.lock:
            logger.debug('Feed back %s %s %s' % (id(fetchId), fetchId.value, result))
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
            if e not in self.fetched:
                return e
        raise Exception('Not found.')

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
        
        def __len__(self):
            return len(self.queue)
        
        def save(self):
            with open(self.file, 'w') as f:
                for e in self.queue:
                    print(repr(e.value), file=f)
        
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
                    result.append(self.Task(eval(e)))
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
        return defaultdict(int)

from threading import Thread
class TransferThread(Thread):
    def __init__(self, fastBundle, slowBundle, queue):
        Thread.__init__(self)
        self.fastBundle = fastBundle
        self.slowBundle = slowBundle
        self.queue = queue
    
    def run(self):
        while True:
            logger.debug('Fetching task')
            fetchId, task = self.queue.fetch()
            logger.debug('Doing task %s' % task)
            result = self.runTask(task)
            logger.debug('Task result: %s' % result)
            self.queue.feedBack(fetchId, result)
    
    def runTask(self, task):
        try:
            self.runTask2(task)
            return True
        except Exception as e:
            logger.exception(e)
            return False
        
    def runTask2(self, task):
        with self.fastBundle.open(task, 'rb') as f1:
            with self.slowBundle.open(task, 'wb') as f2:
                from pclib import copystream
                copystream(f1, f2)

class FileHook:
    def __init__(self, file, preClose = None, postClose = None):
        self.file = file
        self.preClose = self.denone(preClose)
        self.postClose = self.denone(postClose)
    
    def read(self, limit):
        return self.file.read(limit)
    
    def write(self, data):
        return self.file.write(data)
    
    def close(self):
        try:
            self.preClose()
        finally:
            try:
                self.file.close()
            finally:
                self.postClose()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()
    
    def denone(self, x):
        if x is None:
            def empty():
                pass
            return empty
        else:
            return x