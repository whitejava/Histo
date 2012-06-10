import unittest
from io import BytesIO
from .loader import loader
from .writer import writer

class test(unittest.TestCase):
    def test_load(self):
        s = [(('version',0),
             ('commit_time',(2012,6,9)),
             ('name','sample1'),
             ('last_modify',(2012,6,9,0,11,22,333)),
             ('range',(0,123)),
             ('files',('readme.txt','main.cpp'))),
             (('version',0),
             ('commit_time',(2012,6,9)),
             ('name','sample2'),
             ('last_modify',(2012,6,9,16,17,22,333)),
             ('range',(123,520)),
             ('files',('blue.txt','test.rar')))]
        io = BytesIO()
        with writer(io) as f:
            for e in s:
                f.write(e)
        actual = loader(BytesIO(io.getvalue())).load()
        self.assertEquals(s, actual)