import unittest
from .cipher import cipher
from ._timer import timer

#2012 06 09 0.20145043181969796
class test(unittest.TestCase):
    def test_encrypt(self):
        key = b'0'*32
        c = cipher(key)
        with timer():
            c.encrypt(b'1'*10*1024*1024+b'2')