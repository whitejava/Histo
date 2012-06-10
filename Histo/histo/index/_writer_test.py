import unittest
from io import BytesIO
from .writer import writer
from .bad_commit_error import bad_commit_error

def tobytes(a):
    r=[]
    for i in range(0,len(a),2):
        r.append(int(a[i:i+2],16))
    return bytes(r)

def tohex(b):
    return ''.join(['{:02x}'.format(e) for e in b])

class test(unittest.TestCase):
    sample_code = b"\x00\x00\x00\xaf(('version', 0), ('commit_time', (2012, 6, 9)), ('name', 'sample1'), ('last_modify', (2012, 6, 9, 0, 11, 22, 333)), ('range', (0, 123)), ('files', ('readme.txt', 'main.cpp')))"
    double_code = b"\x00\x00\x00\xaf(('version', 0), ('commit_time', (2012, 6, 9)), ('name', 'sample1'), ('last_modify', (2012, 6, 9, 0, 11, 22, 333)), ('range', (0, 123)), ('files', ('readme.txt', 'main.cpp')))\x00\x00\x00\xb0(('version', 0), ('commit_time', (2012, 6, 9)), ('name', 'sample2'), ('last_modify', (2012, 6, 9, 16, 17, 22, 333)), ('range', (123, 520)), ('files', ('blue.txt', 'test.rar')))"
    
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
    
    sample1 = (('version',0),
                ('commit_time',(2012,6,9)),
                ('name','sample1'),
                ('last_modify',(2012,6,9,0,11,22,333)),
                ('range',(0,123)),
                ('files',('readme.txt','main.cpp')))

    sample2 = (('version',0),
                ('commit_time',(2012,6,9)),
                ('name','sample2'),
                ('last_modify',(2012,6,9,16,17,22,333)),
                ('range',(123,520)),
                ('files',('blue.txt','test.rar')))