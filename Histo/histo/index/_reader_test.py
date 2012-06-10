import unittest
from io import BytesIO
from ._reader import reader
from .writer import writer
from ._test_common import common

def tobytes(a):
    return bytes([int(a[i:i+2],16)for i in range(0,len(a),2)])

class test(unittest.TestCase):
    s = common().sample
    
    def setUp(self):
        x = BytesIO()
        with writer(x) as f:
            f.write(self.s)
        self.data = x.getvalue()
    
    def test_read(self):
        with reader(BytesIO(self.data)) as f:
            self.assertEquals(self.s,f.read())
    
    def test_length_error(self):
        b = BytesIO(tobytes('000000ff')+b'[]')
        with self.assertRaises(Exception):
            with reader(b) as f:
                f.read()
    
    def test_format_error(self):
        b = BytesIO(tobytes('00000002')+b'[]')
        with self.assertRaises(Exception):
            with reader(b) as f:
                f.read()
    
    def test_eof(self):
        b = BytesIO()
        with reader(b) as f:
            self.assertEquals(f.read(), None)