import unittest
from io import BytesIO
from .writer import writer
from .bad_commit_error import bad_commit_error
from ._test_common import common

def tobytes(a):
    r=[]
    for i in range(0,len(a),2):
        r.append(int(a[i:i+2],16))
    return bytes(r)

def tohex(b):
    return ''.join(['{:02x}'.format(e) for e in b])

class test(unittest.TestCase):
    sample_code = b"\x00\x00\x00\xbe(('version', 0), ('commit_time', (2012, 6, 9, 0, 0, 0, 123456)), ('name', 'Test'), ('last_modify', (2012, 6, 9, 1, 1, 1, 123456)), ('range', (0, 3)), ('files', ('Reader.java', 'reader.py')))"
    double_code = b"\x00\x00\x00\xbe(('version', 0), ('commit_time', (2012, 6, 9, 0, 0, 0, 123456)), ('name', 'Test'), ('last_modify', (2012, 6, 9, 1, 1, 1, 123456)), ('range', (0, 3)), ('files', ('Reader.java', 'reader.py')))\x00\x00\x00\xc1(('version', 0), ('commit_time', (2012, 6, 9, 0, 0, 0, 123456)), ('name', 'Sample2'), ('last_modify', (2012, 6, 7, 1, 1, 1, 123456)), ('range', (0, 3)), ('files', ('Reader.java', 'reader.py')))"
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
            with self.assertRaises(bad_commit_error):
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