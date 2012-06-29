class bundle:
    def __init__(self, base, cipher):
        self._base = base
        self._cipher = cipher
    
    def dump(self, id, data):
        if type(data) is not bytes:
            raise TypeError('dump data type error')
        code = self._cipher.encode(data)
        return self._base.dump(id, code)
    
    def load(self, id):
        code = self._base.load(id)
        return self._cipher.decode(code)
    
    def exists(self, id):
        return self._base.exists(id)