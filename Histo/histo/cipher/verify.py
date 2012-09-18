class Verify:
    def __init__(self, algorithm):
        self.bundle = bundle
        self.algorithm = algorithm
    
    def encrypt(self):
        return VerifyWriter(self.algorithm)
    
    def decrypt(self):
        return VerifyReader(self.algorithm)
    
class