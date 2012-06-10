import unittest
from .cipher import cipher
from ._timer import timer

#2012 06 09 0.20145043181969796
#2012 06 11 0.20845242799156374
class test(unittest.TestCase):
    def test_encrypt(self):
        c = cipher(bytes(32))
        for _ in range(10):
            with timer():
                c.encrypt(b'1'*10*1024*1024+b'2')