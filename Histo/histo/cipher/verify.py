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

def test():
    import io
    b = io.BytesIO()
    c = Verify('md5')
    a = c.encrypt()
    b.write(a.update(b'123456'))
    b.write(a.final())
    print(b.getvalue())
    c = c.decrypt()
    for e in b.getvalue():
        print(c.update(bytes([e])))
    print(c.final())

if __name__ == '__main__':
    test()