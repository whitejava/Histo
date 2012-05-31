defaultPartSize = 1000000

class State:
    def __init__(self, root, partSize = defaultPartSize):
        self.root = root
        self.partSize = partSize
        self.modified = False
    
    def loadOrCreate(self):
        if self.exists():
            self.load()
        else:
            self.create()
    
    def exists(self):
        import os
        return os.path.exists(self.subfile('state'))
    
    def load(self):
        with open(self.subfile('state'), 'r') as f:
            m = eval(f.read())
            self.partSize = m['partSize']
            self.fileSize = m['fileSize']
            self.buffer = m['buffer']
    
    def create(self):
        import os
        if not os.path.exists(self.root):
            os.makedirs(self.root)
        self.fileSize = 0
        self.buffer = b''
    
    def increaseFileSize(self, delta):
        self.fileSize += delta
        self.modified = True
    
    def close(self):
        if self.modified:
            self.save()
    
    def save(self):
        with open(self.subfile('state'), 'w') as f:
            f.write(repr({'partSize': self.partSize,
                          'fileSize': self.fileSize,
                          'buffer': self.buffer}))
            
    def subfile(self, name):
        import os
        return os.path.join(self.root, name)

class Writer:
    def __init__(self,state,files):
        self.state = state
        self.files = files.openForWrite
        self.modify = set()
    
    def write(self, b):
        self.state.buffer += b
        partId = self.state.fileSize//self.state.partSize
        flushCount = len(self.state.buffer)//self.state.partSize
        for i in range(flushCount):
            part = self.state.buffer[:self.state.partSize]
            self.flushPart(partId+i, part)
            self.state.buffer = self.state.buffer[self.state.partSize:]
        self.state.increaseFileSize(len(b))

    def getModify(self):
        return sorted(self.modify)

    def flushPart(self, partId, part):
        file = self.files(partId)
        try:
            file.write(part)
        finally:
            file.close()
        self.modify.add(partId)
    
    def tell(self):
        return self.state.fileSize
    
    def close(self):
        self.flush()
        self.state.close()
    
    def flush(self):
        if self.state.buffer:
            self.flushPart(self.state.fileSize//self.state.partSize, self.state.buffer)
    
    def __enter__(self):
        return self
    
    def __exit__(self,*k):
        self.close()

class Reader:
    def __init__(self,state,files):
        self.state = state
        self.files = files.openForRead
        self.part = None
        self.pointer = 0
    
    def read(self, limit = None):
        if limit == None or limit > self.available():
            limit = self.available()
        r = b''
        while limit:
            self.ensurePart()
            partRemain = self.state.partSize - self.pointer%self.state.partSize
            readSize = min(partRemain, limit)
            read = self.part.file.read(readSize)
            if len(read) != readSize:
                raise IOError('read length not enough')
            self.pointer += readSize
            r += read
            limit -= readSize
        return r
            
    def seek(self, pos):
        self.pointer = pos
    
    def available(self):
        return self.state.fileSize - self.pointer
    
    def close(self):
        self.closePart()
        self.state.close()
        
    def closePart(self):
        if self.part:
            self.part.file.close()
            self.part = None

    def ensurePart(self):
        if not self.part:
            self.openPart()
        expectPartId = self.pointer//self.state.partSize
        if self.part.id != expectPartId:
            self.openPart()
        actual = self.part.file.tell()
        expect = self.pointer % self.state.partSize
        if actual > expect:
            self.openPart()
            actual = self.part.file.tell()
        if actual < expect:
            self.skipPart(expect - actual)
    
    def skipPart(self, length):
        if len(self.part.file.read(length)) != length:
            raise IOError('Not enough data to skip')
    
    def getFileSize(self):
        return self.state.fileSize
    
    def openPart(self):
        self.closePart()
        class Part:
            pass
        self.part = Part()
        self.part.id = self.pointer//self.state.partSize
        self.part.file = self.files(self.part.id)
        
    def __enter__(self):
        return self
    
    def __exit__(self,*k):
        self.close()
        
class MissingPart(IOError):
    pass

class DataCorrupt(IOError):
    pass

class DecryptError(Exception):
    pass