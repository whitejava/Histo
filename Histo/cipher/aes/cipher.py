from Crypto.Cipher import AES

def _encode(key, iv, data):
    return AES.new(key, AES.MODE_CBC, iv).encrypt(data)

def _decode(key, iv, data):
    return AES.new(key, AES.MODE_CBC, iv).decrypt(data)

class cipher:
    def __init__(self, key):
        if type(key) != bytes:
            raise Exception('key type error')
        if len(key) != 32:
            raise Exception('key length error')
        from Crypto.Cipher import AES
        self._key = key
        self._block_size = AES.block_size

    def encrypt(self, b):
        iv = self._get_random_iv()
        return self._encrypt_wrap_iv(b, iv)
    
    def decrypt(self, data):
        if type(data) is not bytes:
            raise TypeError('decrypt input type error')
        if len(data) < self._block_size:
            raise ValueError('decrypt input length error')
        if len(data) % self._block_size:
            raise ValueError('decrypt input length error')
        iv = data[:self._block_size]
        data = data[self._block_size:]
        return self._decrypt_with_iv(data, iv)
    
    def _get_random_iv(self):
        from Crypto.Random.random import randint
        return bytes([randint(0,255) for _ in range(self._block_size)])
    
    def _encrypt_wrap_iv(self, b, iv):
        code = self._encrypt_with_iv(b, iv)
        return iv + code
    
    def _encrypt_with_iv(self, b, iv):
        padding = self._padding(b)
        return self._encrypt_with_iv_no_padding(padding, iv)
    
    def _encrypt_with_iv_no_padding(self, b, iv):
        cipher = self._get_cipher(iv)
        return cipher.encrypt(b)
    
    def _get_cipher(self, iv):
        from Crypto.Cipher import AES
        return AES.new(self._key, AES.MODE_CBC, iv)
    
    def _decrypt_with_iv(self,b,iv):
        text = self._decrypt_with_iv_no_padding(b, iv)
        return self._unpadding(text)
    
    def _decrypt_with_iv_no_padding(self,b,iv):
        cipher = self._get_cipher(iv)
        return cipher.decrypt(bytes(b))
    
    def _padding(self,b):
        return self._get_padding().encode(b)
    
    def _unpadding(self,b):
        return self._get_padding().decode(b)
    
    def _get_padding(self):
        from ._pkcs7padding import padding
        return padding(self._block_size)