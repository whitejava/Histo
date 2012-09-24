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
        from threading import RLock
        self.lock = RLock()
    
    def open(self, name, mode):
        with self.lock:
            if mode == 'wb':
                return self.openForWrite(name)
            elif mode == 'rb':
                return self.openForRead(name)
            else:
                raise Exception('No such mode.')
    
    def list(self):
        logger.debug('List')
        with self.lock:
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
        result = self.fastBundle.open(name, 'wb')
        def onClose(close0):
            with self.lock:
                self.queue.append(name)
                close0()
                self.limitBufferSize()
        return FileHook(result, onClose=onClose)
    
    def openForRead(self, name):
        if self.fastBundle.exists(name):
            logger.debug('Read from cache')
            return self.fastBundle.open(name, 'rb')
        else:
            logger.debug('Read from slow bundle')
            return self.openSlowBundleForRead(name)
            
    def openSlowBundleForRead(self, name):
        result = FileShell()
        def threadProc():
            from histo.bundle.safe import SafeProtection
            try:
                logger.debug('Reading slow file %s' % name)
                file = self.fetchSlowFileForRead(name)
                logger.debug('Finish read slow %s' % name)
                result.fill(file)
            except SafeProtection as e:
                logger.debug('Read failed %s: %s' % (name, repr(e)))
                result.fail()
            except:
                logger.debug('Read failed %s' % name)
                result.fail()
                raise
        from threading import Thread
        Thread(target=threadProc).start()
        return result
    
    def fetchSlowFileForRead(self, name):
        logger.debug('Fetching slow file %s' % name)
        with self.slowBundle.open(name, 'rb') as f1:
            logger.debug('Opened slow file')
            with self.fastBundle.protect(name):
                logger.debug('Protected fast bundle')
                with self.fastBundle.openIgnoreProtection(name, 'wb') as f2:
                    logger.debug('Opened fast file')
                    logger.debug('Copying')
                    from pclib import copystream
                    copystream(f1, f2)
                    logger.debug('Finish copying')
                result = self.fastBundle.openIgnoreProtection(name, 'rb')
                logger.debug('Reopen fast file')
                return result
    
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
                fileSize = self.fastBundle.getSize(e)
                if self.deleteCache(e):
                    currentBufferSize -= fileSize
    
    def deleteCache(self, file):
        if file in self.queue:
            logger.debug('%s is in queue, should not delete' % file)
            return False
        from histo.bundle.safe import SafeProtection
        try:
            self.fastBundle.delete(file)
            logger.debug('Delete %s ok' % file)
            return True
        except SafeProtection as e:
            logger.debug('Delete %s failed: %s' % (file, repr(e)))
        except Exception as e:
            logger.exception(e)
            logger.debug('Delete %s failed' % file)
            return False

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
        return map(lambda x:x.value, iter(self.queue))
    
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
        from histo.bundle.safe import SafeProtection
        try:
            self.runTask2(task)
            return True
        except SafeProtection as e:
            logger.debug(repr(e))
            return False
        except Exception as e:
            logger.exception(e)
            return False
        
    def runTask2(self, task):
        with self.fastBundle.open(task, 'rb') as f1:
            with self.slowBundle.open(task, 'wb') as f2:
                from pclib import copystream
                copystream(f1, f2)

class FileHook:
    def __init__(self, file, onClose = None):
        self.file = file
        #self.preClose = self.denone(preClose)
        self.onClose = self.denone(onClose)
        #self.postClose = self.denone(postClose)
    
    def read(self, limit):
        return self.file.read(limit)
    
    def write(self, data):
        return self.file.write(data)
    
    def close(self):
        self.onClose(self.file.close)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()
    
    def denone(self, x):
        if x is None:
            def empty(*k):
                pass
            return empty
        else:
            return x

class FileShell:
    def __init__(self):
        from threading import Event
        self.event = Event()
        self.file = None
    
    def fill(self, file):
        logger.debug('Fill')
        self.file = file
        self.event.set()
    
    def fail(self):
        logger.debug('Fail')
        self.event.set()
    
    def read(self, limit):
        self.waitFill()
        return self.read(limit)
    
    def write(self, data):
        self.waitFill()
        return self.file.write(data)
    
    def close(self):
        self.waitFill()
        return self.file.close()
    
    def __enter__(self):
        self.waitFill()
        return self.file.__enter__()
    
    def __exit__(self, *k):
        self.waitFill()
        return self.file.__exit__(*k)
    
    def waitFill(self):
        logger.debug('Waiting filling')
        self.event.wait()
        if self.file is None:
            raise Exception('File shell failed')