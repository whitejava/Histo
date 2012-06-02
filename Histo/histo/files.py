defaultIdFormat = '{:04d}'.format

class MissingPart(Exception):
    pass

class _MonitorWriter:
    def __init__(self, n, file):
        self.n = n
        self.file = file
        print('open writer {}'.format(n))
    
    def write(self, b):
        print('write {} len={}'.format(self.n, len(b)))
        self.file.write(b)
    
    def tell(self):
        r = self.file.tell()
        print('writer {} tell {}'.format(self.n, r))
        return r
    
    def close(self):
        print('close {}'.format(self.n))
        return self.file.close()

class _MonitorReader:
    def __init__(self, n, file):
        self.n = n
        self.file = file
        print('open read {}'.format(n))
    
    def read(self, limit):
        r = self.file.read(limit)
        print('reader {} read limit={}, result len={}'.format(self.n, limit, len(r)))
        return r
    
    def seek(self, pos):
        print('reader {} seek {}'.format(self.n, pos))
        return self.file.seek(pos)
    
    def tell(self):
        r = self.file.tell()
        print('reader {} tell {}'.format(self.n, r))
        return r
    
    def close(self):
        print('reader {} close'.format(self.n))
        return self.file.close()

class MonitorFiles:
    def __init__(self, files):
        self.files = files
    
    def openForWrite(self, n):
        return _MonitorWriter(n, self.files.openForWrite(n))
    
    def openForRead(self, n):
        return _MonitorReader(n, self.files.openForRead(n))

class LocalFiles:
    def __init__(self, root, idFormat = defaultIdFormat):
        self.root = root
        self.idFormat = idFormat
    
    def openForWrite(self, n):
        fileName = self.getFileName(n)
        return open(fileName, 'wb')
    
    def openForRead(self, n):
        fileName = self.getFileName(n)
        if not self.existFile(fileName):
            raise MissingPart
        return open(fileName, 'rb')
    
    def existFile(self, fileName):
        import os
        return os.path.exists(fileName)
    
    def getFileName(self, n):
        import os
        return os.path.join(self.root, self.idFormat(n))

class EncryptFile:
    def __init__(self, file, encrypter):
        self.file = file
        self.encrypter = encrypter
    
    def write(self,b):
        code = self.encrypter.update(b)
        self.file.write(code)
    
    def tell(self):
        return self.file.tell()
    
    def close(self):
        code = self.encrypter.final()
        self.file.write(code)
        self.file.close()
        
class BytesBuffer:
    def __init__(self):
        self.queue = []
        self.pointer = 0
    
    def write(self, b):
        if b:
            self.queue.append(b)
    
    def read(self, limit = None):
        if limit is None:
            limit = self.available()
        r = bytearray()
        while limit and self.queue:
            read = self.readQueue(limit)
            r.extend(read)
            limit -= len(read)
        return r
    
    def currentAvailable(self):
        if not self.queue:
            return 0
        r = len(self.queue[0]) - self.pointer
        return r
    
    def available(self):
        if not self.queue:
            return 0
        r = 0
        for e in self.queue:
            r += len(e)
        return r - self.pointer
    
    def readQueue(self, limit):
        if self.currentAvailable() <= limit:
            return self.popQueue()
        else:
            return self.readCurrent(limit)
        
    def popQueue(self):
        r = self.queue[0][self.pointer:]
        del self.queue[0]
        self.pointer = 0
        return r
    
    def readCurrent(self, limit):
        start = self.pointer
        end = start + limit
        r = self.queue[0][start:end]
        self.pointer += len(r)
        return r
        
class DecryptFile:
    bufferSize = 1024*1024
    
    def __init__(self, file, decrypter):
        self.file = file
        self.decrypter = decrypter
        self.buffer = BytesBuffer()
        self.pointer = 0

    def read(self, limit):
        while self.buffer.available() < limit:
            if not self.supplyBuffer():
                break
        r = self.buffer.read(limit)
        self.pointer += len(r)
        return r
    
    def tell(self):
        return self.pointer
    
    def supplyBuffer(self):
        if not self.decrypter:
            return False
        if not self.file:
            return False
        read = self.file.read(self.bufferSize)
        if not read:
            self.close()
            self.buffer.write(self.finalizeDecrypter())
            return True
        else:
            self.buffer.write(self.decrypter.update(read))
            return True

    def finalizeDecrypter(self):
        r = self.decrypter.final()
        self.decrypter = None
        return r

    def close(self):
        if self.file:
            self.file.close()
            self.file = None
    
    def readBuffer(self, limit):
        if not limit:
            limit = len(self.buffer)
        r = self.buffer[:limit]
        del self.buffer[:limit]
        return r

class CipherFiles:
    def __init__(self, files, cipher):
        self.files = files
        self.cipher = cipher
    
    def openForWrite(self, n):
        file = self.files.openForWrite(n)
        encrypter = self.cipher.encrypter()
        return EncryptFile(file, encrypter)
    
    def openForRead(self, n):
        file = self.files.openForRead(n)
        decrypter = self.cipher.decrypter()
        return DecryptFile(file, decrypter)
    
import unittest
import random

class TestBytesBuffer(unittest.TestCase):
    def testWrite(self):
        return
        for _ in range(10):
            self.bulkWrite()
    
    def testRead(self):
        buffer = BytesBuffer()
        writePointer = 0
        readPointer = 0
        for _ in range(100000):
            length = self.randomLength()
            if self.randomBoolean():
                buffer.write(self.getData(range(writePointer,writePointer+length)))
                writePointer += length
            else:
                read = buffer.read(length)
                expect = self.getData(range(readPointer, readPointer+len(read)))
                if read != expect:
                    raise Exception('data corrupted, expect={}, actual={}'.format(list(expect),list(read)))
                readPointer += len(read)
                if len(read) != length:
                    if buffer.available():
                        raise Exception('data not read fully.')
    
    def bulkWrite(self):
        buffer = BytesBuffer()
        pointer = 0
        for _ in range(1000):
            length = self.randomLength()
            buffer.write(self.getData(range(pointer, length)))
            pointer += length
    
    def randomLength(self):
        return random.randint(0,40)
    
    def getData(self, ra):
        return bytes([e%256 for e in ra])
    
    def randomBoolean(self):
        return random.randint(0,1)==1

if __name__ == '__main__':
    unittest.main()