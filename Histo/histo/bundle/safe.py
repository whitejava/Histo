class Safe:
    def __init__(self, bundle):
        self.bundle = bundle
        self.writing = []
        self.reading = []
        self.files = bundle.list()
        from threading import RLock
        self.lock = RLock()
        self.protection = []
        
    def open(self, name, mode):
        with self.lock:
            self.assertNotProtected(name)
            return self.openIgnoreProtection(name, mode)
    
    def delete(self, name):
        with self.lock:
            self.assertNotProtected(name)
            self.assertNotUsing(name)
            self.bundle.delete(name)
            self.files.remove(name)
    
    def getSize(self, name):
        return self.bundle.getSize(name)
    
    def exists(self, name):
        with self.lock:
            self.assertNotProtected(name)
            return self.bundle.exists(name)
    
    def list(self):
        with self.lock:
            return self.files[:]
    
    def openIgnoreProtection(self, name, mode):
        with self.lock:
            if mode == 'wb':
                return self.openForWrite(name)
            elif mode == 'rb':
                return self.openForRead(name)
            else:
                raise Exception('No such mode')
    
    def protect(self, name):
        self2 = self
        class Result:
            def __enter__(self):
                self2.protection.append(name)
            def __exit__(self, *k):
                self2.protection.remove(name)
        return Result()
    
    def openForWrite(self, name):
        with self.lock:
            self.assertNotUsing(name)
            self.writing.append(name)
            try:
                result = self.bundle.open(name, 'wb')
            except:
                self.writing.remove(name)
                raise
            def postClose():
                with self.lock:
                    if name not in self.files:
                        self.files.append(name)
                    self.writing.remove(name)
            return FileHook(result, postClose = postClose)
    
    def openForRead(self, name):
        with self.lock:
            self.assertNotWriting(name)
            self.reading.append(name)
            try:
                result = self.bundle.open(name, 'rb')
            except:
                self.reading.remove(name)
                raise
            def postClose():
                self.reading.remove(name)
            return FileHook(result, postClose = postClose)
    
    def assertNotUsing(self, name):
        self.assertNotReading(name)
        self.assertNotWriting(name)
    
    def assertNotReading(self, name):
        if name in self.reading:
            raise SafeProtection('%s is reading' % name)
    
    def assertNotWriting(self, name):
        if name in self.writing:
            raise SafeProtection('%s is writing' % name)
        
    def assertNotProtected(self, name):
        if name in self.protection:
            raise SafeProtection('%s is protected' % name)

class SafeProtection(Exception):
    pass

class FileHook:
    def __init__(self, file, postClose):
        self.file = file
        self.postClose = postClose
    
    def read(self, limit):
        return self.file.read(limit)
    
    def write(self, data):
        return self.file.write(data)
    
    def close(self):
        try:
            self.file.close()
        finally:
            self.postClose()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()