class cipher:
    def __init__(self, key):
        if type(key) != bytes:
            raise Exception('key type error')
        if len(key) != 32:
            raise Exception('key length error')
        self._key = key

    def encrypt(self, b):
        iv = self._random_iv()
        return self._encrypt_wrap_iv(b, iv)
    
    def _encrypt_wrap_iv(self, b, iv):
        code = self._encrypt_with_iv(b,iv)
        return iv + code
    
    def _encrypt_with_iv(self, b, iv):
        padding = self._padding(b)
        return self._encrypt_with_iv_no_padding(padding, iv)
    
    def _encrypt_with_iv_no_padding(self, b, iv):
        from Crypto.Cipher import AES
        c = AES.new(self._key, AES.MODE_CBC, iv)
        return c.encrypt(b)
    
    def _random_iv(self):
        from Crypto.Random.random import randint
        from Crypto.Cipher import AES
        return bytes([randint(0,255) for _ in range(AES.block_size)])
    
    def decrypt(self, b):
        if type(b) is not bytes:
            raise TypeError('decrypt input type error')
        from Crypto.Cipher import AES
        if len(b) < AES.block_size:
            raise ValueError('decrypt input length error')
        if len(b) % AES.block_size:
            raise ValueError('decrypt input length error')
        iv = b[:AES.block_size]
        b = b[AES.block_size:]
        return self._decrypt_with_iv(b, iv)
    
    def _decrypt_with_iv(self,b,iv):
        text = self._decrypt_with_iv_no_padding(b, iv)
        return self._unpadding(text)
    
    def _decrypt_with_iv_no_padding(self,b,iv):
        from Crypto.Cipher import AES
        c = AES.new(self._key, AES.MODE_CBC, bytes(iv))
        return c.decrypt(bytes(b))
    
    def _padding(self,b):
        return self._get_padding().encode(b)
    
    def _unpadding(self,b):
        return self._get_padding().decode(b)
    
    def _get_padding(self):
        from ._pkcs7padding import padding
        from Crypto.Cipher import AES
        return padding(AES.block_size)