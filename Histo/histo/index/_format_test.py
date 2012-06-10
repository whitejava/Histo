import unittest
from ._format import format
from ._test_common import common

class test(unittest.TestCase):
    def setUp(self):
        self.s = list(common().sample)
    
    def test_correct(self):
        self.good()
    
    def test_version(self):
        self.s[0] = ('version', 1)
        self.bad()
    
    def test_commit_time(self):
        self.s[1] = ('commit_time', (2012,1,1,0,0,0,123456))
        self.good()
        self.s[1] = ('commit_time', (2012,))
        self.bad()
        self.s[1] = ('commit_time', ())
        self.bad()
        self.s[1] = ('commit_time', (2012,13,1))
        self.bad()
        self.s[1] = ('commit_time', 1)
        self.bad()
        self.s[1] = ('commit_time', (2011.1, 1))
        self.bad()
    
    def test_name(self):
        self.s[2] = ('name', None)
        self.bad()
        self.s[2] = ('name', 'a')
        self.good()
        self.s[2] = ('name', '')
        self.good()
    
    def test_last_modify(self):
        self.s[3] = ('last_modify', (2012,1,1,1,1,1,123456))
        self.good()
        self.s[3] = ('last_modify', (2012,))
        self.bad()
        self.s[3] = ('last_modify', None)
        self.bad()
    
    def test_range(self):
        self.s[4] = ('range', (0,2))
        self.good()
        self.s[4] = ('range', (-1,10))
        self.bad()
        self.s[4] = ('range', (10,9))
        self.bad()
    
    def test_files(self):
        self.s[5] = ('files', ())
        self.good()
        self.s[5] = ('files', 123)
        self.bad()
        self.s[5] = ('files', (b'bytes'))
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
    
    def test_type_error(self):
        self.s = dict(self.s)
        self.bad()
        
    def good(self):
        self.assertTrue(format().check(tuple(self.s)))
    
    def bad(self):
        self.assertFalse(format().check(tuple(self.s)))