class Safe:
    def __init__(self, bundle):
        self.bundle = bundle
        self.writing = []
        self.reading = []
        self.files = bundle.list()
        from threading import Lock
        self.lock = Lock()
        
    def open(self, name, mode):
        if mode == 'wb':
            return self.openForWrite(name)
        elif mode == 'rb':
            return self.openForRead(name)
        else:
            raise Exception('No such mode')
    
    def delete(self, name):
        with self.lock:
            self.assertNotUsing(name)
            self.bundle.delete(name)
            self.files.remove(name)
    
    def list(self):
        return self.files[:]
    
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
        assert name not in self.reading, '%s is reading' % name
    
    def assertNotWriting(self, name):
        assert name not in self.writing, '%s is writing' % name

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
        return self.file
    
    def __exit__(self, *k):
        self.close()