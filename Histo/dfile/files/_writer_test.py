import unittest
from dfile.bundle.memory.bundle import bundle
from ..files._writer import writer

class test(unittest.TestCase):
    def test_write_twice(self):
        b = bundle()
        with writer(b,0) as f:
            f.write(b'123')
            f.write(b'456')
        assert b.load(0) == b'123456'
    
    def test_overwrite(self):
        b = bundle()
        with writer(b,0) as f:
            f.write(b'123')
        with writer(b,0) as f:
            pass
        assert b.load(0) == b''
    
    def test_write_two_files(self):
        b = bundle()
        with writer(b,0) as f:
            f.write(b'123')
        with writer(b,1) as f:
            f.write(b'456')
        assert b.load(0) == b'123'
        assert b.load(1) == b'456'
        
    def test_before_close(self):
        b = bundle()
        b.dump(0,b'')
        with writer(b,0) as f:
            f.write(b'123')
            assert b.load(0) == b''
        assert b.load(0) == b'123'
        
    def test_double_close(self):
        b = bundle()
        f = writer(b,0);
        f.write(b'123')
        f.close()
        with self.assertRaises(Exception):
            f.close()
            
    def test_write_after_close(self):
        b = bundle()
        f = writer(b,0)
        f.write(b'123')
        f.close()
        with self.assertRaises(Exception):
            f.write(b'234')
