import unittest
from io import BytesIO
from .reader import reader

def tobytes(a):
    return bytes([int(a[i:i+2],16)for i in range(0,len(a),2)])

class test(unittest.TestCase):
    s = [('version', 0),
         ('commit_time',(2012, 6, 9)),
         ('last_modify', (2012, 6, 9, 0, 11, 22, 333)),
         ('range', (0, 123)),
         ('files', ['readme.txt', 'main.cpp'])]
    
    def test_read(self):
        b = BytesIO(tobytes('0000009a') + b"[('version', 0), ('commit_time', (2012, 6, 9)), ('last_modify', (2012, 6, 9, 0, 11, 22, 333)), ('range', (0, 123)), ('files', ['readme.txt', 'main.cpp'])]")
        with reader(b) as f:
            commit = f.read()
        self.assertEquals(commit, self.s)
    
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