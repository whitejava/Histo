import unittest
from io import BytesIO
from .writer import writer
from ._test_common import common

def _expect_error(error):
    from expecterr.expect_error import expect_error
    return expect_error(error)

class test(unittest.TestCase):
    sample_code = b"\x00\x00\x00\xb4(('version', 0), ('time', (2012, 6, 9, 0, 0, 0, 123456)), ('name', 'Test'), ('last-modify', (2012, 6, 9, 1, 1, 1, 123456)), ('range', (0, 3)), ('summary', 'Reader.java reader.py'))"
    double_code = b"\x00\x00\x00\xb4(('version', 0), ('time', (2012, 6, 9, 0, 0, 0, 123456)), ('name', 'Test'), ('last-modify', (2012, 6, 9, 1, 1, 1, 123456)), ('range', (0, 3)), ('summary', 'Reader.java reader.py'))\x00\x00\x00\xb7(('version', 0), ('time', (2012, 6, 9, 0, 0, 0, 123456)), ('name', 'Sample2'), ('last-modify', (2012, 6, 7, 1, 1, 1, 123456)), ('range', (0, 3)), ('summary', 'Writer.java writer.py'))"
    sample1 = common().sample
    sample2 = common().sample2
    
    def test_write(self):
        b = BytesIO()
        with writer(b) as f:
            f.write(self.sample1)
        print(b.getbuffer().tobytes())
        self.assertEquals(b.getbuffer(),self.sample_code)
    
    def test_double_open_double_write(self):
        b = BytesIO()
        with writer(b) as f:
            f.write(self.sample1)
        with writer(b) as f:
            f.write(self.sample2)
        print(b.getbuffer().tobytes())
        self.assertEquals(self.double_code, b.getvalue())
        
    def test_illegal(self):
        b = BytesIO()
        with writer(b) as f:
            with _expect_error('input type error'):
                f.write([])

    def test_write_after_with(self):
        with writer(BytesIO()) as f:
            pass
        f.write(self.sample1)
            
    def test_double_with(self):
        a = writer(BytesIO())
        with a:
            pass
        with a:
            pass