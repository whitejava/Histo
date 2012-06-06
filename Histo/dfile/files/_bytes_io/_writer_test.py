from unittest import TestCase
from .._bytes_io.writer import writer

class test(TestCase):
    def test_write(self):
        data = bytearray()
        with writer(data) as f:
            f.write(b'123')
            f.write(b'456')
        assert data == bytearray(b'123456')
        
    def test_write_bytearray(self):
        data = bytearray()
        with writer(data) as f:
            f.write(bytearray(b'123'))
            f.write(bytearray(b'456'))
        assert data == bytearray(b'123456')
    
    def test_write_based_on_data(self):
        data = bytearray(b'123456')
        with writer(data) as f:
            f.write(b'789')
        assert data == b'123456789'
        
    def test_write_empty(self):
        data = bytearray()
        with writer(data) as f:
            f.write(b'')
        assert data == b''