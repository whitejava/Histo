import unittest
from ..bundle.memory.bundle import bundle
from ._writer import writer

class test(unittest.TestCase):
    def setUp(self):
        self._bundle = self._get_bundle()
    
    def test_write(self):
        self._open_write(b'123')
        self._good_load(b'123')
        
    def test_double_write(self):
        self._open_write([b'123', b'abc'])
        self._good_load(b'123abc')
        
    def test_overwrite(self):
        self._open_write(b'123')
        self._open_write(b'abc')
        self._good_load(b'abc')
    
    def test_write_different_files(self):
        self._open_write(id = 0, input = b'123')
        self._open_write(id = 1, input = b'abc')
        self._good_load(id = 0, expect = b'123')
        self._good_load(id = 1, expect = b'abc')
    
    def _open_write(self, input = b'123', id = 0):
        if type(input) is bytes:
            input = [input]
        with writer(self._bundle, id) as f:
            for e in input:
                f.write(e)
    
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
            
    def test_write_type_error(self):
        with self._expect_error('write input type error'):
            self._open_write([1])
            
    def test_write_id_allow(self):
        self._open_write(id = 1.5)
    
    def _good_load(self, expect = None, id = 0):
        self._output = self._bundle.load(id)
        self._good_output(expect)
        
    def _good_output(self, expect = None):
        if expect is None:
            expect = self._expect
        self.assertEquals(expect, self._output)
    
    def _get_bundle(self):
        from ..bundle.memory.bundle import bundle
        return bundle()
    
    def _expect_error(self, message):
        from expecterr.expect_error import expect_error
        return expect_error(message)