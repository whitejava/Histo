__all__ = ['AES']

class AES:
    def __init__(self, key):
        self.key = key
    
    def encrypt(self):
        return Encrypter(self.key)
    
    def decrypt(self):
        return Decrypter(self.key)

def Encrypter(key):
    from histo.cipher.hub import CipherHub
    iv = randomIv()
    header = OutputHeader(iv)
    cipher = Encrypter2(key, iv)
    padding = Padding()
    blocking = Blocking()
    return CipherHub(Meter(0), padding, Meter(1), blocking, Meter(2), cipher, Meter(3), header, Meter(4))

def Decrypter(key):
    from .hub import CipherHub
    cipher = CipherAgent()
    def onIv(iv):
        cipher.setCipher(Decrypter2(key, iv))
    header = InputHeader(getBlockSize(), onIv)
    unpadding = Unpadding()
    blocking = Blocking()
    return CipherHub(header, blocking, cipher, unpadding)

def randomIv():
    import random
    return bytes([random.randrange(256) for _ in range(getBlockSize())])

class Encrypter2:
    def __init__(self, key, iv):
        self.cipher = Cipher(key, iv)
    
    def update(self, data):
        return self.cipher.encrypt(data)
    
    def final(self):
        return b''

class Decrypter2:
    def __init__(self, key, iv):
        self.cipher = Cipher(key, iv)
    
    def update(self, data):
        return self.cipher.decrypt(data)
    
    def final(self):
        return b''

def Cipher(key, iv):
    import Crypto.Cipher.AES as AES2
    return AES2.new(key, AES2.MODE_CBC, iv)

def getBlockSize():
    import Crypto.Cipher.AES as AES2
    return AES2.block_size

class OutputHeader:
    def __init__(self, data):
        self.data = data
    
    def update(self, data):
        if self.data:
            return self.fetchData() + data
        else:
            return data
    
    def final(self):
        return self.update(b'')
    
    def fetchData(self):
        result = self.data
        self.data = None
        return result

def Padding():
    return PKCS5(getBlockSize())

def Blocking():
    return Blocking2(getBlockSize())

class CipherAgent:
    def __init__(self, cipher = None):
        self.cipher = cipher
    
    def update(self, data):
        return self.cipher.update(data)
    
    def final(self):
        return self.cipher.final()
    
    def setCipher(self, cipher):
        self.cipher = cipher

class InputHeader:
    def __init__(self, headerSize, onHeader):
        self.headerSize = headerSize
        self.onHeader = onHeader
        self.header = b''
    
    def update(self, data):
        if self.header is not None:
            self.header += data
            self.header = self.header[:self.headerSize]
            result = self.header[self.headerSize:]
            if len(self.header) == self.headerSize:
                self.onHeader(self.header)
                self.header = None
            return result
        else:
            return data
    
    def final(self):
        assert self.header is None, 'Header not enough'
        return b''

class Unpadding:
    def __init__(self, blockSize):
        self.blockSize = blockSize
        self.lastBytes = b''
    
    def update(self, data):
        self.lastBytes += data
        result = self.lastBytes[:-self.blockSize]
        self.lastBytes = self.lastBytes[-self.blockSize:]
        return result
    
    def final(self):
        paddingSize = self.lastBytes[-1]
        assert len(self.lastBytes) >= paddingSize, 'Bad padding size'
        result = self.lastBytes[:-paddingSize]
        padding = self.lastBytes[-paddingSize:]
        assert padding == bytes([paddingSize]*paddingSize), 'Bad padding'
        return result

class PKCS5:
    def __init__(self, blockSize):
        self.blockSize = blockSize
        self.dataLength = 0
        
    def update(self, data):
        self.dataLength += len(data)
        return data
    
    def final(self):
        minPadding = 1
        paddingSize = ((self.blockSize-self.dataLength)-minPadding) % self.blockSize + minPadding
        return bytes([paddingSize]*paddingSize)

class Blocking2:
    def __init__(self, blockSize):
        self.blockSize = blockSize
        self.buffer = b''
        
    def update(self, data):
        self.buffer += data
        remain = len(self.buffer) % self.blockSize
        result = self.buffer[:-remain]
        self.buffer = self.buffer[-remain:]
        return result
    
    def final(self):
        assert not self.buffer, 'Data is not blocked.'

class Meter:
    def __init__(self, name):
        self.name = name
    
    def update(self, data):
        from base64 import b16encode
        print(self.name, 'update', str(b16encode(data)))
        return data
    
    def final(self):
        print(self.name, 'final')
        return b''

def test():
    key = b'1'*32
    cipher = AES(key)
    import io
    from base64 import b16encode
    buffer = io.BytesIO()
    a = cipher.encrypt()
    for i in range(2):
        x = a.update(bytes([i]*i))
        buffer.write(x)
        print(b16encode(x))
    x = a.final()
    buffer.write(x)
    print(b16encode(x))
    print('Decode')
    a = cipher.decrypt()
    for e in buffer.getvalue():
        print(b16encode(a.update(bytes([e]))))
    print(b16encode(a.final()))

if __name__ == '__main__':
    test()