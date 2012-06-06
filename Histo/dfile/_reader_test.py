import unittest
from unittest import TestCase
from reader import reader
from writer import writer
from bundle.bundle import bundle
from files.memory.memory_files import memory_files as files

class test(TestCase):
    def __init__(self,a):
        TestCase.__init__(self,a)
    
    def test_read(self):
        with self._reader(b'123') as f:
            assert f.read() == b'123'
    
    def test_double_read(self):
        with self._reader(b'1234') as f:
            assert f.read(3) == b'123'
            assert f.read(1) == b'4'
    
    def test_read_too_much(self):
        with self._reader(b'123') as f:
            assert f.read(5) == b'123'
    
    def test_read_empty(self):
        with self._reader(b'123') as f:
            assert f.read(0) == b''
    
    def test_read_from_empty(self):
        with self._reader(b'') as f:
            assert f.read() == b''
    
    def test_seek(self):
        with self._reader(b'123') as f:
            f.seek(2)
            assert f.read(2) == b'3'
    
    def test_reseek(self):
        with self._reader(b'1234567') as f:
            f.seek(5)
            assert f.read(2) == b'67'
            f.seek(2)
            assert f.read(3) == b'345'
    
    def _reader(self, data, part_size = 2):
        b = bundle()
        with writer(b, part_size) as f:
            f.write(data)