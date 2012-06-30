from Crypto.Cipher import AES
from Crypto.Random import random
from .padding import pkcs7padding

__all__ = ['cipher']

def _encode(key, iv, data):
    return AES.new(key, AES.MODE_CBC, iv).encrypt(data)

def _decode(key, iv, data):
    return AES.new(key, AES.MODE_CBC, iv).decrypt(data)

def _randomiv(length):
    #Random bytes in specified length.
    return bytes([random.randint(0,255)for _ in range(length)])

class cipher:
    def __init__(self, key):
        self._key = key
    
    def encode(self, data):
        #Random iv
        iv = _randomiv(AES.block_size)
        #Encode
        data = _encode(self._key, iv, pkcs7padding.encode(data))
        #Wrap iv
        return iv + data
    
    def decode(self, data):
        #Unwrap iv
        iv, data = data[:AES.block_size], data[AES.block_size:]
        #Decode
        return pkcs7padding.decode(_decode(self._key, iv, data))