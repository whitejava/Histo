import unittest
from ..memory.bundle import bundle
from .bundle import bundle as crypto
from ._test_cipher import test_cipher as cipher
from ._decrypt_error import decrypt_error

class test(unittest.TestCase):
    def test_dump(self):
        b = bundle()
        c = crypto(b, cipher())
        c.dump(0, b'12345')
        assert b.load(0) == b'a12345b'
    
    def test_load(self):
        b = bundle()
        b.dump(0,b'a12345b')
        c = crypto(b, cipher())
        assert c.load(0) == b'12345'
        
    def test_mix(self):
        b = bundle()
        c = crypto(b,cipher())
        c.dump(0,b'12345')
        assert c.load(0) == b'12345'
    
    def test_decrypt_error(self):
        b = bundle()
        b.dump(0,b'12345')
        c = crypto(b,cipher())
        with self.assertRaises(decrypt_error):
            c.load(0)