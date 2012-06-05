import unittest
from unittest import TestCase
from writer import writer

class test(TestCase):
    def test_dump(self):
        d = {}
        with writer(d, 0) as f:
            f.dump(b'1234')
        assert d == {0:b'1234'}
    
    def test_overwrite(self):
        d = {}
        with writer(d, 1) as f:
            f.dump(b'567')
            f.dump(b'1234')
        assert d == {1:b'1234'}

unittest.main()