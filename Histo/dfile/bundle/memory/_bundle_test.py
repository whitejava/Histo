import unittest

from ..memory.bundle import bundle

class test(unittest.TestCase):
    def test_dump(self):
        lib = bundle()
        lib.dump(0,b'123')
    
    def test_load(self):
        lib = bundle()
        lib.dump(0,b'123')
        assert lib.load(0) == b'123'
    
    def test_load_not_exist(self):
        lib = bundle()
        with self.assertRaises(KeyError):
            lib.load(1)
    
    def test_exists(self):
        lib = bundle()
        assert lib.exists(0) == False
        lib.dump(0,b'123')
        assert lib.exists(0) == True
        
    def test_delete(self):
        b = bundle()
        b.dump(0,b'123')
        b.delete(0)
        assert not b.exists(0)
