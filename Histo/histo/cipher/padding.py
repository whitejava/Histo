class Padding:
    def __init__(self, size):
        self.size = size
        
    def encrypt(self):
        return Encrypter(self.size)
    
    def decrypt(self):
        pass
    
class Encrypter:
    def __init__(self, size):
        pass
    
    def update(self, data):
        pass
    
    def final(self, data):
        pass
    
class Decrypter:
    def __init__(self):