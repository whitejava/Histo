from Crypto.Cipher import AES
from Crypto.Random import random
import pkcs7padding

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

def test():
    key = b'a'*16
    iv = b'a'*16
    data = b'abc'*16
    from timer import timer
    with timer():
        for i in range(100):
            a=b'a'*1024*1024
            cipher = AES.new(key, AES.MODE_CBC, iv)
            x1 = cipher.encrypt(b'a'*1024*1024)
    x2 = cipher.encrypt(data)
    cipher2 = AES.new(key, AES.MODE_CBC, iv)
    print(cipher2.decrypt(x2))