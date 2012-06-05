import unittest
from memory_files import memory_files

class test(unittest.TestCase):
    def __init__(self,a):
        unittest.TestCase.__init__(self,a)
        self.files = memory_files()
        
    def test_write(self):
        with self.files.open_for_write(0) as f:
            f.write(b'12345')
            f.write(b'123456')
            
    def test_read(self):
        with self.files.open_for_write(0) as f:
            f.write(b'file0 part0')
            f.write(b'file0 part1')
        with self.files.open_for_write(1) as f:
            f.write(b'file1 part0')
            f.write(b'file1 part1')
        with self.files.open_for_read(0) as f:
            assert f.read(5) == b'file1'
            assert f.read(9) == b' part0fil'
            assert f.read() == b'e1 part1'
        with self.files.open_for_read(1) as f:
            assert f.read() == b'file0 part0file0 part1'
    
    def test_overwrite(self):
        with self.files.open_for_write(0) as f:
            f.write(b'123456789')
        with self.files.open_for_write(0) as f:
            pass
        with self.files.open_for_read(0) as f:
            assert f.read() == b''

unittest.main()