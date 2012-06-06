from .bundle.memory.bundle import bundle
from .bundle.broken.bundle import bundle as broken
from .files.files import files
from .writer import writer
import unittest

class test(unittest.TestCase):
    def test_just_open_close(self):
        b = bundle()
        fs = files(b)
        with writer(fs, 2):
            pass
        assert b.load(0) == self._header(0,2,b'')
        assert b.exists(1) == False
    
    def test_write_bit(self):
        b = bundle()
        with writer(files(b),2) as f:
            f.write(b'1')
        assert b.load(0) == self._header(1,2,b'1')
        assert b.load(1) == b'1'
        assert not b.exists(2)
    
    def test_write_part_size(self):
        b = bundle()
        fs = files(b)
        with writer(fs,2) as f:
            f.write(b'12')
        assert b.load(0) == self._header(2,2,b'')
        assert b.load(1) == b'12'
        assert not b.exists(2)
    
    def test_write_interpart(self):
        b = bundle()
        with writer(files(b), 2) as f:
            f.write(b'12345')
        assert b.load(0) == self._header(5,2,b'5')
        assert b.load(1) == b'12'
        assert b.load(2) == b'34'
        assert b.load(3) == b'5'
        assert not b.exists(4)
    
    def test_double_write(self):
        b = bundle()
        with writer(files(b),2) as f:
            f.write(b'1')
            f.write(b'23')
        assert b.load(0) == self._header(3,2,b'3')
        assert b.load(1) == b'12'
        assert b.load(2) == b'3'
        assert not b.exists(3)
    
    def test_double_open(self):
        b = bundle()
        with writer(files(b),2) as f:
            f.write(b'123')
        assert b.load(0) == self._header(3,2,b'3')
        assert b.load(1) == b'12'
        assert b.load(2) == b'3'
        assert not b.exists(3)
        with writer(files(b),2) as f:
            f.write(b'4')
        assert b.load(0) == self._header(4,2,b'')
        assert b.load(1) == b'12'
        assert b.load(2) == b'34'
        assert not b.exists(3)
    
    def test_write_lost_part(self):
        b = bundle()
        with writer(files(b),2) as f:
            f.write(b'1')
        b.delete(1)
        with writer(files(b),2) as f:
            f.write(b'2')
        assert b.load(0) == self._header(2,2,b'')
        assert b.load(1) == b'12'
        assert not b.exists(2)
    
    def test_write_empty(self):
        b = bundle()
        with writer(files(b),2) as f:
            f.write(b'12')
            f.write(b'')
        assert b.load(0) == self._header(2,2,b'')
        assert b.load(1) == b'12'
        assert not b.exists(2)

    def test_write_failed(self):
        b = broken(bundle(), [2])
        with writer(files(b),2) as f:
            f.write(b'12')
        with writer(files(b),2) as f:
            f.write(b'3')
        assert b.load(0) == self._header(2,2,b'')
        assert b.load(1) == b'12'

    def test_double_with(self):
        b = bundle()
        w = writer(files(b),2)
        with w: pass
        with self.assertRaises(Exception):
            with w: pass

    def test_write_after_with(self):
        b = bundle()
        w = writer(files(b),2)
        with w: pass
        with self.assertRaises(Exception):
            w.write(b'123')
            
    def _header(self,*k):
        d = dict(zip(['file_size','part_size','cache'],[k[0],k[1],bytearray(k[2])]))
        import pickle
        return pickle.dumps(d)