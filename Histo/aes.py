from Crypto.Cipher import AES
import pkcs7padding, os

__all__ = ['cipher']

def _encode(key, iv, data):
    return AES.new(key, AES.MODE_CBC, iv).encrypt(data)

def _decode(key, iv, data):
    return AES.new(key, AES.MODE_CBC, iv).decrypt(data)

class cipher:
    def __init__(self, key):
        self._key = key
    
    def encode(self, data):
        iv = os.urandom(AES.block_size)
        data = _encode(self._key, iv, pkcs7padding.encode(data))
        return iv + data
    
    def decode(self, data):
        iv, data = data[:AES.block_size], data[AES.block_size:]
        return pkcs7padding.decode(_decode(self._key, iv, data))