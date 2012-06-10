import unittest
from io import BytesIO
from ._reader import reader
from .writer import writer

def tobytes(a):
    return bytes([int(a[i:i+2],16)for i in range(0,len(a),2)])

class test(unittest.TestCase):
    s = (('version', 0),
         ('commit_time',(2012, 6, 9)),
         ('name','sample'),
         ('last_modify', (2012, 6, 9, 0, 11, 22, 333)),
         ('range', (0, 123)),
         ('files', ('readme.txt', 'main.cpp')))
    
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