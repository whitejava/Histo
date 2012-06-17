class cipher:
    def __init__(self):
        self._prefix = b'a'
        self._postfix = b'b'
    
    def encrypt(self, data):
        if type(data) is not bytes:
            raise TypeError('encrypt input type error')
        return self._prefix + data + self._postfix
    
    def decrypt(self, data):
        if type(data) is not bytes:
            raise TypeError('decrypt input type error')
        if len(data) < 2:
            raise ValueError('decrypt input length error')
        if data[0] != ord(self._prefix) or data[-1] != ord(self._postfix):
            raise ValueError('decrypt input value error')
        return data[1:-1]
