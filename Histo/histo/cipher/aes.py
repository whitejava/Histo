__all__ = ['AES']

class AES:
    def __init__(self, key):
        self.key = key
    
    def encrypt(self):
        return Encrypter(self.key)
    
    def decrypt(self):
        return Decrypter(self.key)

class Encrypter:
    def __init__(self, key):
        self.iv = randomIv()
        self.wrapper = OutputAtFirstTime(self.iv)
        self.cipher = createCipher(key, self.iv)
        self.padding = createPadding()

    def update(self, data):
        data = self.padding.update(data)
        cipherData = self.cipher.encrypt(data)
        return self.wrapper.update(cipherData)
    
    def final(self):
        data = self.padding.final()
        return self.wrapper.final(self.update(data))

class Decrypter:
    def __init__(self, key):
        self.key = key
        
    def update(self, data):
        pass
    
    def final(self):
        pass

def randomIv():
    import random
    return bytes([random.randrange(256) for _ in range(getBlockSize())])

def createCipher(key, iv):
    import Crypto.Cipher.AES as AES2
    return AES2.new(key, AES2.MODE_CBC, iv)

def createPadding():
    from .padding import PKCS5
    return PKCS5(getBlockSize())

def getBlockSize():
    import Crypto.Cipher.AES as AES2
    return AES2.block_size

class OutputAtFirstTime:
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