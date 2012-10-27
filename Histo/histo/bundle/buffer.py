__all__ = ['Buffer']

from debuginfo import *
import logging
logger = logging.getLogger()

class Buffer:
    def __init__(self, config, fastBundle, slowBundle, exitSignal):
        with DebugInfo('Initialize buffer bundle'):
            self.config = config
            from histo.bundle import Safe
            self.exitSignal = exitSignal
            self.fastBundle = Safe(fastBundle)
            from histo.bundle import ListCache
            self.slowBundle = ListCache(slowBundle, config['ListInterval'], exitSignal)
            from threading import RLock
            self.lock = RLock()
            self.usageLog = self.getUsageLog(config['UsageLogFile'])
            self.queue = TaskQueue()
            self.threads = self.createTransferThreads(config['ThreadCount'])
            self.protectedFiles = []
            for e in self.threads:
                e.start()
            def supplyNotUploaded():
                self.queue.extend(self.getNotUploadedFiles())
            from threading import Thread
            Thread(target = supplyNotUploaded).start()
    
    def open(self, name, mode):
        with self.lock:
            with DebugInfo('Open %s with mode %r' % (name, mode)):
                if mode == 'wb':
                    return self.openForWrite(name)
                elif mode == 'rb':
                    return self.openForRead(name)
                else:
                    raise Exception('No such mode.')
    
    def list(self):
        with DebugInfo('List') as d:
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
                d.result = str(len(result))
                return result
    
    def listFast(self):
        with DebugInfo('List fast'):
            return self.fastBundle.list()
    
    def delete(self, name):
        raise Exception('Not support.')
    
    def protect(self, name):
        with DebugInfo('Protect %s' % name):
            self.protectedFiles.append(name)
    
    def unprotect(self, name):
        with DebugInfo('Unprotect: %s' % name):
            self.protectedFiles.remove(name)
    
    def getNotUploadedFiles(self):
        with DebugInfo('Get not uploaded files') as d:
            fastFiles = self.fastBundle.list()
            slowFiles = self.slowBundle.list()
            for e in slowFiles:
                fastFiles.remove(e)
            d.result = 'Count: %d' % len(fastFiles)
            return fastFiles
    
    def getUsageLog(self, usageLogFile):
        with DebugInfo('Get usage log'):
            return UsageLog(usageLogFile)
    
    def createTransferThreads(self, threadCount):
        with DebugInfo('Create transfer threads'):
            return [self.createTransferThread() for _ in range(threadCount)]
        
    
    def openForWrite(self, name):
        with DebugInfo('Open for write %s' % name):
            result = self.fastBundle.open(name, 'wb')
            def onClose(close0):
                with DebugInfo('Close %s' % name):
                    with self.lock:
                        self.queue.append(name)
                        close0()
                        self.limitBufferSize()
            return FileHook(result, onClose=onClose)
    
    def openForRead(self, name):
        with DebugInfo('Open for read: %s' % name) as d:
            self.usageLog.log(name)
            if self.fastBundle.exists(name):
                d.result = 'From cache'
                return self.fastBundle.open(name, 'rb')
            else:
                d.result = 'From slow'
                return self.openSlowBundleForRead(name)
            
    def openSlowBundleForRead(self, name):
        result = FileShell()
        def threadProc():
            from histo.bundle.safe import SafeProtection
            try:
                with DebugInfo('Read slow file %s' % name):
                    file = self.fetchSlowFileForRead(name)
                result.fill(file)
            except SafeProtection as e:
                logger.debug('Read failed %s: %s' % (name, repr(e)))
                result.fail()
            except Exception as e:
                logger.debug('Read failed %s' % name)
                result.fail()
                logger.debug(e)
        from threading import Thread
        Thread(target=threadProc).start()
        return result
    
    def fetchSlowFileForRead(self, name):
        with DebugInfo('Fetching slow file %s' % name):
            with DebugInfo('Open slow file'):
                slowFile = self.slowBundle.open(name, 'rb')
            with slowFile as f1:
                with DebugInfo('Protect %s' % name):
                    protection = self.fastBundle.protect(name)
                with protection:
                    with DebugInfo('Open fast file'):
                        fastFile = self.fastBundle.openIgnoreProtection(name, 'wb')
                    with fastFile as f2:
                        with DebugInfo('Copy'):
                            from pclib import copystream2
                            copystream2(f1, f2)
                    with DebugInfo('Reopen fast file'):
                        result = self.fastBundle.openIgnoreProtection(name, 'rb')
                    return result
    
    def createTransferThread(self):
        with DebugInfo('Create transfer thread'):
            return TransferThread(self.fastBundle, self.slowBundle, self.queue, self.exitSignal)
    
    def limitBufferSize(self):
        with DebugInfo('Limit buffer size'):
            with self.lock:
                currentBufferSize = self.fastBundle.getTotalSize()
                mostUseless = self.getMostUseless()
                for e in mostUseless:
                    if currentBufferSize <= self.config['MaxBufferSize']:
                        break
                    fileSize = self.fastBundle.getSize(e)
                    if self.deleteCache(e):
                        currentBufferSize -= fileSize
    
    def deleteCache(self, file):
        if file in self.protectedFiles:
            logger.debug('%s is in protection, should not be deleted' % file);
            return False
        if file not in self.slowBundle.listWithCache():
            logger.debug('%s may not uploaded, it should not be deleted' % file)
            return False
        from histo.bundle.safe import SafeProtection
        try:
            self.fastBundle.delete(file)
            logger.debug('Delete %s ok' % file)
            return True
        except SafeProtection as e:
            logger.debug('Delete %s failed: %s' % (file, repr(e)))
            return False
        except Exception as e:
            logger.exception(e)
            logger.debug('Delete %s failed' % file)
            return False
    
    def getMostUseless(self):
        with DebugInfo('Get most useless'):
            files = self.fastBundle.list()
            files = [(-self.usageLog.getUsageCount(e), e) for e in files]
            files = sorted(files)
            files = [e[1] for e in files]
            return files

class TaskQueue:
    def __init__(self):
        self.queue = []
        self.fetched = []
        from threading import Lock, Semaphore
        self.semaphore = Semaphore(len(self.queue))
        self.lock = Lock()
    
    def __iter__(self):
        return map(lambda x:x.value, iter(self.queue))
    
    def append(self, x):
        with DebugInfo('Append %s' % x):
            with self.lock:
                self.queue.append(Task(x))
                self.semaphore.release()
        
    def extend(self, iterable):
        for e in iterable:
            self.append(e)
        
    def fetch(self, exitSignal):
        with DebugInfo('Fetch') as d:
            while not exitSignal.is_set():
                if self.semaphore.acquire(timeout=0.5):
                    with self.lock:
                        task = self.findUnfetch()
                        self.fetched.append(task)
                        d.result = 'Fetch %s %s' % (id(task), task.value)
                        return task, task.value
            raise OnExitSignal()
    
    def feedBack(self, fetchId, result):
        with DebugInfo('Feed back %s %s' % (fetchId, result)):
            with self.lock:
                self.fetched.remove(fetchId)
                if result:
                    self.queue.remove(fetchId)
                else:
                    self.semaphore.release()
            
    def findUnfetch(self):
        for e in self.queue:
            if e not in self.fetched:
                return e
        raise Exception('Not found.')
    
class Task:
    def __init__(self, value):
        self.value = value

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
        with open(self.file, 'a', encoding = 'utf8') as f:
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
    def __init__(self, fastBundle, slowBundle, queue, exitSignal):
        Thread.__init__(self)
        self.fastBundle = fastBundle
        self.slowBundle = slowBundle
        self.queue = queue
        self.exitSignal = exitSignal
    
    def run(self):
        try:
            while not self.exitSignal.is_set():
                logger.debug('Fetching task')
                fetchId, task = self.queue.fetch(self.exitSignal)
                logger.debug('Doing task %s' % task)
                result = self.runTask(task)
                logger.debug('Task result: %s' % result)
                self.queue.feedBack(fetchId, result)
        except OnExitSignal:
            logger.debug('On exit signal, exiting')
    
    def runTask(self, task):
        from histo.bundle.safe import SafeProtection
        from histo.bundle.mail import MailDeniedException
        try:
            self.runTask2(task)
            return True
        except SafeProtection as e:
            logger.debug(repr(e))
            return False
        except MailDeniedException as e:
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
        return self.file.read(limit)
    
    def write(self, data):
        self.waitFill()
        return self.file.write(data)
    
    def close(self):
        logger.debug('Close')
        self.waitFill()
        return self.file.close()
    
    def __enter__(self):
        logger.debug('Enter')
        self.waitFill()
        return self
    
    def __exit__(self, *k):
        logger.debug('Exit')
        self.waitFill()
        self.close()
    
    def waitFill(self):
        if not self.event.is_set():
            logger.debug('Waiting filling')
        self.event.wait()
        if self.file is None:
            raise Exception('File shell failed')

class OnExitSignal(Exception):
    pass