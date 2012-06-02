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
        
class DecryptFile:
    bufferSize = 1024*1024
    
    def __init__(self, file, decrypter):
        self.file = file
        self.decrypter = decrypter
        self.buffer = bytearray()
        self.pointer = 0

    def read(self, limit):
        if limit == None:
            raise IOError('not limit')
            r = b''
            while True:
                r += self.readBuffer()
                if not self.supplyBuffer():
                    self.pointer += len(r)
                    return r
        else:
            r = b''
            while limit:
                read = self.readBuffer(limit)
                r += read
                limit -= len(read)
                if not limit:
                    break
                if not self.supplyBuffer():
                    break
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
            self.buffer += self.finalizeDecrypter()
            return True
        else:
            self.buffer += self.decrypter.update(read)
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
        self.buffer = self.buffer[limit:]
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