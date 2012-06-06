from unittest import TestCase
from .reader import reader

class test(TestCase):
    def test_read_all(self):
        with reader(b'1234') as f:
            assert f.read() == b'1234'
    
    def test_read_limited(self):
        with reader(b'123456') as f:
            assert f.read(4) == b'1234'
    
    def test_read_parts(self):
        with reader(b'123456') as f:
            assert f.read(4) == b'1234'
            assert f.read(2) == b'56'
            
    def test_read_eof(self):
        with reader(b'123') as f:
            assert f.read(5) == b'123'
            assert f.read() == b''
            assert f.read(11) == b''
    
    def test_read_zero_length(self):
        with reader(b'123') as f:
            assert f.read(0) == b''
            
    def test_read_from_empty(self):
        with reader(b'') as f:
            assert f.read(11) == b''
            assert f.read() == b''
            
    def test_read_from_bytearray(self):
        data = bytearray(b'1234')
        with reader(data) as f:
            data[2] = ord('5')
            assert f.read() == b'1234'
    
    def test_seek(self):
        with reader(b'123456') as f:
            f.seek(2)
            assert f.read(2) == b'34'
            f.seek(1)
            assert f.read(3) == b'234'
            f.seek(3)
            assert f.read() == b'456'
            f.seek(6)
            assert f.read() == b''
    
    def test_seek_out_of_file(self):
        with self.assertRaises(IOError):
            with reader(b'123456') as f:
                f.seek(7)