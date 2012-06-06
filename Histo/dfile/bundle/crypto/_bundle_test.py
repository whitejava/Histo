import unittest
from ..memory.bundle import bundle
from .bundle import bundle as crypto

def tohex(b):
    return ''.join(['{:02x}'.format(e) for e in b])

def tobytes(s):
    return bytes([int(s[i:i+2],16) for i in range(0, len(s), 2)])

class test(unittest.TestCase):
    def test_dump(self):
        b = bundle()
        ci = cipher
        c = crypto(b, ci)
        c.dump(0,b'12345')
        assert tohex(b.load(0)) == '000000'
    
    def test_load(self):
        b = bundle()
        b.dump(0,tobytes('000000'))
        ci = 
        c = crypto(b)
        assert tohex(c.load(0)) == '12345'
        
    def test_mix(self):
        b = bundle()
        c = crypto(b)
        c.dump(0,b'12345',seed=1)
        assert c.load(0) == b'12345'
    
    def test_mix_random_iv(self):
        b = bundle()
        c = crypto(b)
        c.dump(0,b'12345')
        print('encrypted text:',tohex(b.load(0)))
        assert c.load(0) == b'12345'