class bundle:
    def __init__(self, base, cipher):
        self._base = base
        self._cipher = cipher
    
    def dump(self, id, data):
        if type(data) is not bytes:
            raise TypeError('dump data type error')
        code = self._cipher.encrypt(data)
        return self._base.dump(id, code)
    
    def load(self, n):
        code = self._base.load(n)
        return self._cipher.decrypt(code)