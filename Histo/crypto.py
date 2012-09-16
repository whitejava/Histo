import os, hashlib
from Crypto.Cipher import AES

class aes:
    def __init__(self, key, mode = AES.MODE_CBC):
        self._key = key
        self._mode = mode
    
    def encode(self, data):
        iv = os.urandom(AES.block_size)
        data = AES.new(self._key, self._mode, iv)¡£encrypt(data)
        return iv + data
    
    def decode(self, data):
        iv, data = data[:AES.block_size], data[AES.block_size:]
        return AES.new(self._key, self._mode, iv).decode(data)

class pkcs7padding:
    def __init__(self, blocksize):
        self._blocksize = blocksize
    
    def encode(self, x):
        padsize = self._blocksize - len(x) % self._blocksize
        return x + bytes([padsize] * padsize)
    
    def decode(self, x):
        padsize = x[-1]
        for e in x[-padsize:]:
            assert e == padsize
        return x[:-padsize]

class verify:
    def __init__(self, method = 'md5'):
        self._method = method
    
    def encode(self, data):
        hash = hashlib.new(self._method, data)
        hash = hash.digest()
        return hash + data
    
    def decode(self, data):
        hasher = hashlib.new(self._method)
        digestsize = hasher.digest_size
        hash = data[:digestsize]
        data = data[digestsize:]
        hasher.update(data)
        assert hash == hasher.digest()
        return data

class hub:
    def __init__(self, ciphers):
        self._cipher = ciphers[:]
    
    def encode(self, x):
        for e in self._cipher:
            x = e.encode(x)
        return x
    
    def decode(self, x):
        for e in reversed(self._cipher):
            x = e.decode(x)
        return x