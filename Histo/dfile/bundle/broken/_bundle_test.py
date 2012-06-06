import unittest
from ..broken.bundle import bundle as broken
from ..memory.bundle import bundle

class test(unittest.TestCase):
    def test_normal(self):
        b = broken(bundle(), [1])
        b.dump(0,b'123')
        assert b.load(0) == b'123'
    
    def test_broken(self):
        b = broken(bundle(),[1])
        with self.assertRaises(Exception):
            b.dump(1,b'123')
