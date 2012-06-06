import unittest
from ..bundle.memory.bundle import bundle
from ._reader import reader

class test(unittest.TestCase):
    def setUp(self):
        b = bundle()
        b.dump(0,b'123456')
        self.reader = reader(b,0)
    
    def test_read(self):
        with self.reader as f:
            assert f.read(2) == b'12'
    
    def test_read_all(self):
        with self.reader as f:
            assert f.read() == b'123456'
    
    def test_seek(self):
        with self.reader as f:
            f.seek(2)
            assert f.read(2) == b'34'
    
    def test_seek_out_of_file(self):
        with self.reader as f:
            with self.assertRaises(Exception):
                f.seek(7)
                
    def test_double_close(self):
        self.reader.close()
        with self.assertRaises(Exception):
            self.reader.close()
    
    def test_read_after_close(self):
        self.reader.close()
        with self.assertRaises(Exception):
            self.reader.read()
    
    def test_seek_after_close(self):
        self.reader.close()
        with self.assertRaises(Exception):
            self.reader.seek(1)
