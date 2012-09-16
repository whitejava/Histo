class Safe:
    def __init__(self, bundle):
        self.bundle = bundle
        self.writing = []
        self.reading = []
        
    def open(self, name, mode):
        if mode == 'wb':
            return self.openForWrite(name)
        elif mode == 'rb':
            return self.openForRead(name)
        else:
            raise Exception('No such mode')
    
    def delete(self, name):
        if name in self.writing or name in self.reading:
            raise Exception('File is using.')
        self.bundle.delete(name)
    
    def list(self):
        result = self.bundle.list()
        for e in self.writing:
            if e in result:
                result.remove(e)
        return result
    
    def openForWrite(self, name):
        if name in self.reading:
            raise Exception('File is reading')
        result = self.bundle.open(name, 'wb')
        close0 = result.close
        def close2():
            close0()
            self.writing.remove(name)
        result.close = close2
        return result
    
    def openForRead(self, name):
        if name in self.writing:
            raise Exception('File is writing')
        result = self.bundle.open(name, 'rb')
        close0 = result.close
        def close2():
            close0()
            self.reading.remove(name)
        result.close = close2
        return result