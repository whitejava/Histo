__all__ = ['Verify']

class Verify:
    def __init__(self, algorithm):
        self.algorithm = algorithm
    
    def encrypt(self):
        return Encrypter(self.algorithm)
    
    def decrypt(self):
        return Decrypter(self.algorithm)
    
class Encrypter:
    def __init__(self, algorithm):
        import hashlib
        self.hasher = hashlib.new(algorithm)
    
    def update(self, data):
        self.hasher.update(data)
        return data
    
    def final(self):
        return self.hasher.digest()

class Decrypter:
    def __init__(self, algorithm):
        import hashlib
        self.hasher = hashlib.new(algorithm)
        self.end = b''
    
    def update(self, data):
        self.end += data
        result = self.end[:-self.hasher.digest_size]
        self.end = self.end[-self.hasher.digest_size:]
        self.hasher.update(result)
        return result
    
    def final(self):
        assert self.hasher.digest() == self.end, 'Verify failed.'
        return b''