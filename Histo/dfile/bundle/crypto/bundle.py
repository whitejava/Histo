class bundle:
    def __init__(self, base, cipher):
        self._base = base
        self._cipher = cipher
    
    def dump(self,n,b):
        code = self._cipher.encrypt(b)
        return self._base.dump(n,code)
    
    def load(self,n):
        code = self._base.load(n)
        return self._cipher.decrypt(code)