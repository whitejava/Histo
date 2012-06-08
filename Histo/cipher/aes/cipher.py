from Crypto.Cipher import AES
from .bad_padding_error import bad_padding_error
from ..decrypt_error import decrypt_error

class cipher:
    def __init__(self,key):
        if len(key) != 32:
            raise Exception('key length error')
        self._key = key
        self._block_size = 16

    def encrypt(self,b):
        iv = self._random_iv()
        return self._encrypt_wrap_iv(b,iv)
    
    def _encrypt_wrap_iv(self,b,iv):
        r = bytearray(iv)
        r.extend(self._encrypt_with_iv(b,iv))
        return r
    
    def _encrypt_with_iv(self,b,iv):
        self._encrypt_with_iv_no_padding(self._padding(b), iv)
    
    def _encrypt_with_iv_no_padding(self,b,iv):
        c = AES.new(self._key, AES.MODE_CBC, iv)
        return c.encrypt(b)
    
    def _random_iv(self):
        from Crypto.Random.random import randint
        return bytes([randint(0,255) for _ in range(AES.block_size)])
    
    def decrypt(self,b):
        if len(b) < AES.block_size:
            raise decrypt_error()
        iv = b[:AES.block_size]
        b = b[AES.block_size:]
        return self._decrypt_with_iv(b,iv)
    
    def _decrypt_with_iv(self,b,iv):
        return self._unpadding(self._decrypt_with_iv_no_padding(b, iv))
    
    def _decrypt_with_iv_no_padding(self,b,iv):
        c = AES.new(self._key, AES.MODE_CBC, bytes(iv))
        return c.decrypt(bytes(b))
    
    def _padding(self,b):
        need = AES.block_size - len(b)%AES.block_size
        return b+bytes([need]*need)
    
    def _unpadding(self,b):
        if len(b) == 0:
            raise bad_padding_error()
        padding_size = b[-1]
        if not padding_size in range(1,17):
            raise bad_padding_error()
        text = b[:-padding_size]
        padding = b[-padding_size:]
        for e in padding:
            if e != padding_size:
                raise bad_padding_error()
        return text