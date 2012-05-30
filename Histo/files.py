defaultIdFormat = '{:04d}'.format

class LocalFiles:
    def __init__(self, root, idFormat = defaultIdFormat):
        self.root = root
        self.idFormat = idFormat
    
    def openForWrite(self, n):
        fileName = self.getFileName(n)
        return open(fileName, 'wb')
    
    def openForRead(self, n):
        fileName = self.getFileName(n)
        return open(fileName, 'rb')
        
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
    bufferSize = 8192
    
    def __init__(self, file, decrypter):
        self.file = file
        self.decrypter = decrypter
        self.buffer = b''
    
    def read(self, limit):
        if not limit:
            r = b''
            while True:
                r += self.readBuffer()
                if not self.supplyBuffer():
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
            return r
    
    def supplyBuffer(self):
        if not self.decrypter:
            return False
        if not self.file:
            return False
        read = self.file.read(self.bufferSize)
        if not read:
            self.buffer += self.decrypter.final()
            self.file.close()
            self.file = None
            return True
        else:
            self.buffer += self.decrypter.update(read)
            return True
        
    def close(self):
        if self.file:
            self.decrypter.final()
            self.file.close()
            self.file = None
            
    def tell(self):
        return self.file.tell()
    
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