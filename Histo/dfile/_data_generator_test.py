import unittest
import random
from _data_generator import data_generator

class test(unittest.TestCase):
    def __init__(self,a):
        unittest.TestCase.__init__(self,a)
        self.d = data_generator()
    
    def test_data_permanent(self):
        s = [self._random_range(100) for _ in range(1000)]
        assert self._read_ranges(s) == self._read_ranges(s)
    
    def _random_range(self,size):
        a = random.randint(0,size)
        b = random.randint(0,size)
        if a > b:
            a,b = b,a
        return range(a,b)
    
    def _read_ranges(self,ranges):
        return [self._read_range(e) for e in ranges]
    
    def _read_range(self,ra):
        if not ra:
            return b''
        self.d.seek(ra[0])
        return self.d.read(len(ra))

if __name__ == '__main__':
    unittest.main()