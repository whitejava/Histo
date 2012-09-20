class Hub:
    def __init__(self, *ciphers):
        self.ciphers = ciphers
    
    def encrypt(self):
        return CipherHub(*[e.encrypt() for e in self.ciphers])
    
    def decrypt(self):
        return CipherHub(*reversed([e.decrypt() for e in self.ciphers]))

class CipherHub:
    def __init__(self, *ciphers):
        self.ciphers = ciphers
    
    def update(self, data):
        for e in self.ciphers:
            data = e.update(data)
        return data
    
    def final(self):
        result = b''
        for e in self.ciphers:
            result = e.update(result)
            result = result + e.final()
        return result