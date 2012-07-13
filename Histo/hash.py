__all__ = ['cipher']

import hashlib

class cipher:
    def __init__(self, method = 'md5'):
        self._method = method
    
    def encode(self, data):
        hash = hashlib.new(self._method, data)
        hash = hash.digest()
        return hash + data
    
    def decode(self, data):
        hasher = hashlib.new(self._method)
        digestsize = hasher.digest_size
        hash = data[:digestsize]
        data = data[digestsize:]
        hasher.update(data)
        assert hash == hasher.digest()
        return data