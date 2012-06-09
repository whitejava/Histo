import unittest
from _format import format

class test(unittest.TestCase):
    def setUp(self):
        self.s = [('version', 0),
                  ('commit_time',(2012,6,9)),
                  ('last_modify',(2012,6,9,1,1,1)),
                  ('range',(0,3)),
                  ('files',['Reader.java', 'reader.py'])]
    
    def test_correct(self):
        self.good()
    
    def test_version(self):
        self.s[0] = ('version', 1)
        self.bad()
    
    def test_commit_time(self):
        self.s[1] = ('commit_time', (2012,))
        self.good()
        self.s[1] = ('commit_time', ())
        self.bad()
        self.s[1] = ('commit_time', (2012,13,1))
        self.good()
        self.s[1] = ('commit_time', 1)
        self.bad()
        self.s[1] = ('commit_time', (2011.1, 1))
        self.bad()
    
    def test_last_modify(self):
        self.s[2] = ('last_modify', (2012,))
        self.good()
        self.s[2] = ('last_modify', None)
        self.bad()
    
    def test_range(self):
        self.s[3] = ('range', (0,2))
        self.good()
        self.s[3] = ('range', (-1,10))
        self.bad()
        self.s[3] = ('range', (10,9))
        self.bad()
    
    def test_files(self):
        self.s[4] = ('files', [])
        self.good()
        self.s[4] = ('files', 123)
        self.bad()
        self.s[4] = ('files', [b'bytes'])
        self.bad()
    
    def test_item_error(self):
        self.s[0] = ('version', 1, 2)
        self.bad()
    
    def test_unknown_item(self):
        self.s[0] = ('unknown', 1)
        self.bad()
    
    def test_disorder(self):
        self.s[2],self.s[3] = self.s[3],self.s[2]
        self.bad()
    
    def test_more_item(self):
        self.s.append(('more', 0))
        self.bad()
    
    def test_less_item(self):
        del self.s[-1]
        self.bad()
    
    def test_not_commit(self):
        self.s = dict(self.s)
        self.bad()
        
    def good(self):
        self.assertTrue(format().check(self.s))
    
    def bad(self):
        self.assertFalse(format().check(self.s))