import unittest
from .lister import lister

class test(unittest.TestCase):
    def test_normal(self):
        expect = ['2','1.txt','2\\3.txt']
        self.assertEquals(expect, self._list('normal'))
    
    def test_embed(self):
        expect = ['1.txt', '2.rar', '2.rar>>3.txt']
        self.assertEquals(expect, self._list('embed'))
    
    def test_part_unlistable(self):
        expect = ['2','1.txt','2\\3.rar']
        self.assertEquals(expect, self._list('part_unlistable'))
        
    def test_unlistable(self):
        expect = []
        self.assertEquals(expect, self._list('unlistable'))
        
    def test_encrypt(self):
        expect = []
        self.assertEquals(expect, self._list('encrypt'))
    
    def test_part_encrypt(self):
        expect = ['1.txt','2.rar']
        self.assertEquals(expect, self._list('part_encrypt'))
    
    def test_hidden(self):
        expect = ['1.jpg','2.jpg'] # 2.jpg contains hidden file, but cannot detect.
        self.assertEquals(expect, self._list('hidden'))

    def test_list_dir(self):
        import os
        expect = ['embed','empty','embed\\a','embed\\file','embed\\a\\file']
        path = os.path.join(os.path.dirname(__file__), '_dir_test')
        li = lister._list_dir(None, path)
        self.assertEquals(expect,li)
    
    def _list(self,x):
        import os
        filename = os.path.join(os.path.dirname(__file__),'_test_rar',x+'.rar')
        return lister(filename).list()