class VerifyError(Exception):
    pass

class _XorEncrypt:
    def __init__(self,sequence):
        self.s = sequence
        self.firstUpdate = True
    
    def update(self,b):
        extra = b''
        if self.firstUpdate:
            self.firstUpdate = False
            import random
            extra = bytes([random.randint(0,255) for _ in range(self.s.getSeedSize())])
            self.s.setSeed(extra)
        r = bytes([e^next(self.s) for e in b])
        return extra + r
    
    def final(self):
        return b''

class _XorDecrypt:
    def __init__(self,sequence):
        self.s = sequence
        self.seed = b''
        
    def update(self,b):
        seedSize = self.s.getSeedSize()
        if len(self.seed) < seedSize:
            needSize = seedSize - len(self.seed)
            self.seed += b[:needSize]
            b = b[needSize:]
            if len(self.seed) == seedSize:
                self.s.setSeed(self.seed)
        return bytes([e^next(self.s) for e in b])
    
    def final(self):
        return b''

class _HashSequence:
    def __init__(self, key, algorithm = 'md5'):
        self.key = key
        self.algorithm = algorithm
    
    def getSeedSize(self):
        import hashlib
        return hashlib.new(self.algorithm).digest_size
    
    def setSeed(self, seed):
        self.seed = seed
    
    def __next__(self):
        import hashlib
        self.seed = hashlib.new(self.algorithm, self.seed + self.key).digest()
        return self.xor(self.seed)
    
    def xor(self,b):
        r = 0
        for e in b:
            r ^= e
        return r
    
class XorCipher:
    def __init__(self, key, algorithm = 'md5'):
        self.key = key
        self.algorithm = algorithm
    
    def encrypter(self):
        return _XorEncrypt(_HashSequence(self.key, self.algorithm))
    
    def decrypter(self):
        return _XorDecrypt(_HashSequence(self.key, self.algorithm))

class _VerifyEncrypt:
    def __init__(self, algorithm):
        import hashlib
        self.hasher = hashlib.new(algorithm)
    
    def update(self, b):
        self.hasher.update(b)
        return b
    
    def final(self):
        return self.hasher.digest()

class _VerifyDecrypt:
    def __init__(self, algorithm):
        import hashlib
        self.hasher = hashlib.new(algorithm)
        self.hashBytes = b''
    
    def update(self,b):
        self.hashBytes += b
        r = self.hashBytes[:-self.hasher.digest_size]
        self.hashBytes = self.hashBytes[-self.hasher.digest_size:]
        self.hasher.update(r)
        return r
    
    def final(self):
        h = self.hasher.digest()
        if h != self.hashBytes:
            raise VerifyError()
        return b''

class VerifyCipher:
    def __init__(self, algorithm = 'md5'):
        self.algorithm = algorithm
    
    def encrypter(self):
        return _VerifyEncrypt(self.algorithm)
    
    def decrypter(self):
        return _VerifyDecrypt(self.algorithm)