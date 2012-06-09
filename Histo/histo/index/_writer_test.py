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
    sample_code = tobytes('0000009a') + b"[('version', 0), ('commit_time', (2012, 6, 9)), ('last_modify', (2012, 6, 9, 0, 11, 22, 333)), ('range', (0, 123)), ('files', ['readme.txt', 'main.cpp'])]"
    
    def test_write(self):
        b = BytesIO()
        with writer(b) as f:
            f.write(self.sample_commit1())
        print(tohex(b.getbuffer().tobytes()))
        self.assertEquals(b.getbuffer(),self.sample_code)
    
    def test_double_open_double_write(self):
        b = BytesIO()
        with writer(b) as f:
            f.write(self.sample_commit1())
        with writer(b) as f:
            f.write(self.sample_commit2())
            
    def test_illegal(self):
        b = BytesIO()
        with writer(b) as f:
            with self.assertRaises(bad_commit_error):
                f.write([])
    
    def test_none(self):
        with writer(BytesIO()) as f:
            with self.assertRaises(bad_commit_error):
                f.write(None)
    
    def test_version_illegal(self):
        with writer(BytesIO()) as f:
            s = self.sample_commit1()
            s[0]=('version',1)
            with self.assertRaises(bad_commit_error):
                f.write(s)
    
    def test_commit_time(self):
        with writer(BytesIO()) as f:
            s = self.sample_commit1()
            # it's legal
            s[1] = ('commit_time', (2012,6,32))
            f.write(s)
            s[1] = ('commit_time', ())
            with self.assertRaises(bad_commit_error):
                f.write(s)
            s[1] = ('commit_time', 2012)
            with self.assertRaises(bad_commit_error):
                f.write(s)
            s[1] = ('commit_time', (2012,))
            f.write(s)
    
    def test_last_modify(self):
        with writer(BytesIO()) as f:
            s = self.sample_commit1()
            # it's legal
            s[2] = ('last_modify', (2012,6,32))
            f.write(s)
            s[2] = ('last_modify', ())
            with self.assertRaises(bad_commit_error):
                f.write(s)
            s[2] = ('last_modify', 2012)
            with self.assertRaises(bad_commit_error):
                f.write(s)
            s[2] = ('last_modify', (2012,))
            f.write(s)
    
    def test_range(self):
        with writer(BytesIO()) as f:
            s = self.sample_commit1()
            s[3] = ('range',(123))
            with self.assertRaises(bad_commit_error):
                f.write(s)
            s[3] = ('range',123)
            with self.assertRaises(bad_commit_error):
                f.write(s)
    
    def test_files(self):
        with writer(BytesIO()) as f:
            s = self.sample_commit1()
            s[4] = ('files', [])
            f.write(s)
            s[4] = ('files', [123,[456,789]])
            with self.assertRaises(bad_commit_error):
                f.write(s)
    
    def test_disorder(self):
        with writer(BytesIO()) as f:
            s = self.sample_commit1()
            s[1],s[2] = s[2],s[1]
            with self.assertRaises(bad_commit_error):
                f.write(s)

    def test_more_item(self):
        with writer(BytesIO()) as f:
            s = self.sample_commit1()
            s.append(('unknown',123))
            with self.assertRaises(bad_commit_error):
                f.write(s)
    
    def test_less_item(self):
        with writer(BytesIO()) as f:
            s = self.sample_commit1()
            del s[4]
            with self.assertRaises(bad_commit_error):
                f.write(s)

    def test_unknown_item(self):
        with writer(BytesIO()) as f:
            s = self.sample_commit1()
            s[0] = ('unknown',12)
            with self.assertRaises(bad_commit_error):
                f.write(s)
    
    def test_write_after_with(self):
        with writer(BytesIO()) as f:
            pass
        f.write(self.sample_commit1())
            
    def test_double_with(self):
        a = writer(BytesIO())
        with a:
            pass
        with a:
            pass
    
    def sample_commit1(self):
        return [('version',0),
                ('commit_time',(2012,6,9)),
                ('last_modify',(2012,6,9,0,11,22,333)),
                ('range',(0,123)),
                ('files',['readme.txt','main.cpp'])]

    def sample_commit2(self):
        return [('version',0),
                ('commit_time',(2012,6,9)),
                ('last_modify',(2012,6,9,16,17,22,333)),
                ('range',(123,520)),
                ('files',['blue.txt','test.rar'])]