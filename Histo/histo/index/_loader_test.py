import unittest
from io import BytesIO
from .loader import loader

class test(unittest.TestCase):
    def test_load(self):
        code = b"\x00\x00\x00\x9a[('version', 0), ('commit_time', (2012, 6, 9)), ('last_modify', (2012, 6, 9, 0, 11, 22, 333)), ('range', (0, 123)), ('files', ['readme.txt', 'main.cpp'])]\x00\x00\x00\x9b[('version', 0), ('commit_time', (2012, 6, 9)), ('last_modify', (2012, 6, 9, 16, 17, 22, 333)), ('range', (123, 520)), ('files', ['blue.txt', 'test.rar'])]"
        expect = [[('version',0),
             ('commit_time',(2012,6,9)),
             ('last_modify',(2012,6,9,0,11,22,333)),
             ('range',(0,123)),
             ('files',['readme.txt','main.cpp'])],
             [('version',0),
             ('commit_time',(2012,6,9)),
             ('last_modify',(2012,6,9,16,17,22,333)),
             ('range',(123,520)),
             ('files',['blue.txt','test.rar'])]]
        actual = loader(BytesIO(code)).load()
        self.assertEquals(expect, actual)