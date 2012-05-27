defaultPartSize = 1000000
defaultIdFormat = '{:04d}'.format

class DFileState:
    def __init__(self, file, partSize):
        self.file = file
        self.partSize = partSize
        self.fileSize = 0
    
    def loadOrCreate(self):
        if self.exists():
            self.load()
        else:
            self.create()
    
    def load(self):
        with open(self.file, 'r') as f:
            m = eval(f.readline())
            self.fileSize = m['fileSize']
            if self.partSize != m['partSize']:
                raise IOError('partSize is not same')
    
    def create(self):
        pass
    
    def close(self):
        self.save()
    
    def updateLength(self, pos):
        self.fileSize = max(self.fileSize, pos)
    
    def save(self):
        self.createParentDir()
        with open(self.file, 'w') as f:
            f.write(repr({'fileSize':self.fileSize,
                          'partSize':self.partSize}))
    
    def createParentDir(self):
        import os
        root = os.path.dirname(self.file)
        if not os.path.exists(root):
            os.makedirs(root)
    
    def exists(self):
        import os
        return os.path.exists(self.file)
    
class DFileLock:
    def __init__(self, fileName):
        self.fileName = fileName
        if self.exists():
            raise Exception('Failed to lock. Maybe the dfile is in use.')
        self.createLock()
    
    def close(self):
        self.deleteLock()
        
    def exists(self):
        import os
        return os.path.exists(self.fileName)
    
    def createLock(self):
        self.createParentDir(self.fileName)
        open(self.fileName, 'w').close()
    
    def deleteLock(self):
        import os
        os.remove(self.fileName)
        
    def createParentDir(self, fileName):
        import os
        parent = os.path.dirname(fileName)
        if not os.path.exists(parent):
            os.makedirs(parent)

class DFileBase:
    def __init__(self, root, partSize, idFormat):
        self.root = root
        self.partSize = partSize
        self.idFormat = idFormat
        self.pointer = 0
        self.part = None
        self.state = DFileState(self.getStateFileName(), partSize)
        self.lock = DFileLock(self.getLockFileName())
        
    def getCorrectPartId(self):
        return self.pointer // self.partSize
    
    def getCorrectPartPos(self):
        return self.pointer % self.partSize
    
    def tell(self):
        return self.pointer
    
    def seek(self, pos):
        if pos > self.size():
            raise IOError('seek out of bounds')
        self.pointer = pos
    
    def size(self):
        return self.state.fileSize
    
    def close(self):
        self.closePart()
        self.state.close()
        self.lock.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self,t,v,tract):
        self.close()
    
    def getStateFileName(self):
        import os
        return os.path.join(self.root, 'state')
    
    def getCorrectPartFileName(self):
        import os
        return os.path.join(self.root, self.idFormat(self.getCorrectPartId()))
    
    def getLockFileName(self):
        import os
        return os.path.join(self.root, 'lock')
    
    def ensurePart(self):
        if not self.isOnCorrectPart():
            self.openCorrectPart()
    
    def ensurePartPos(self):
        if not self.isOnCorrectPartPos():
            self.seekCorrectPartPos()
    
    def isOnCorrectPart(self):
        if not self.part:
            return False
        if self.part.id != self.getCorrectPartId():
            return False
        return True
    
    def isOnCorrectPartPos(self):
        return self.part.tell() == self.getCorrectPartPos()
        
    def seekCorrectPartPos(self):
        self.part.seek(self.getCorrectPartPos())
        
    def closePart(self):
        if self.part:
            self.part.close()
            self.part = None
            
    def seekEnd(self):
        self.seek(self.state.fileSize)
        
    def getRemainSize(self):
        return self.state.fileSize - self.tell()

class PartBase:
    def __init__(self, id, fileName, size):
        self.id = id
        self.fileName = fileName
        self.size = size
    
    def seek(self, pos):
        import os
        if pos > os.path.getsize(self.fileName):
            raise IOError('target part is missing')
        self.file.seek(pos)
    
    def close(self):
        self.file.close()
    
    def tell(self):
        return self.file.tell()
    
    def getRemainSize(self):
        return self.size - self.tell()

class PartReader(PartBase):
    def __init__(self, id, fileName, size):
        PartBase.__init__(self, id, fileName, size)
        self.file = open(fileName, 'rb')
    
    def read(self, size):
        return self.file.read(size)

class PartWriter(PartBase):
    def __init__(self, id, fileName, size):
        PartBase.__init__(self, id, fileName, size)
        self.file = self.openOrCreate(fileName)
    
    def write(self, b):
        self.file.write(b)
        
    def flush(self):
        self.file.flush()
    
    def openOrCreate(self, fileName):
        import os
        if not os.path.exists(fileName):
            open(fileName, 'wb').close()
        return open(fileName, 'r+b')

class DFileWriter(DFileBase):
    def __init__(self, root, partSize = defaultPartSize, idFormat = defaultIdFormat):
        DFileBase.__init__(self, root, partSize, idFormat)
        self.state.loadOrCreate()
        self.modify = set()
        self.part = None
        self.seekEnd()
    
    def write(self,b):
        while b:
            self.ensurePart()
            self.ensurePartPos()
            s = self.part.getRemainSize()
            self.part.write(b[:s])
            self.modify |= set([self.part.id])
            self.pointer += len(b[:s])
            self.state.updateLength(self.pointer)
            b = b[s:]
    
    def flush(self):
        if self.part:
            self.part.flush()
    
    def openCorrectPart(self):
        self.part = PartWriter(self.getCorrectPartId(), self.getCorrectPartFileName(), self.partSize)
    
    def getModify(self):
        return self.modify

class DFileReader(DFileBase):
    def __init__(self, root, partSize = defaultPartSize, idFormat = defaultIdFormat):
        DFileBase.__init__(self, root, partSize, idFormat)
        self.state.load()
    
    def read(self, limit = None):
        if not limit:
            limit = self.getRemainSize()
        else:
            limit = min(limit, self.getRemainSize())
        r = b''
        while limit:
            self.ensurePart()
            self.ensurePartPos()
            s = min(limit, self.part.getRemainSize())
            read = self.part.read(s)
            if not read:
                break
            r += read
            limit -= len(read)
            self.pointer += len(read)
        return r
    
    def openCorrectPart(self):
        self.part = PartReader(self.getCorrectPartId(), self.getCorrectPartFileName(), self.partSize)

def writeSample():
    with DFileWriter('D:\\dfile', 10) as f:
        for i in range(2):
            f.write(b'0123456789abcdefghijkl')
    print(f.getModify())
    
def readSample():
    with DFileReader('D:\\dfile', 10) as f:
        print(f.read())

readSample()