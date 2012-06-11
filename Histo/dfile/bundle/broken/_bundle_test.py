import unittest

class test(unittest.TestCase):
    def test_no_broken(self):
        self._broken([])
        self._good_dump(0)
        
    def test_avoid_broken(self):
        self._broken([1])
        self._good_dump(0)
    
    def test_one_broken(self):
        self._broken([1])
        self._bad_dump(1, 'target is broken')
    
    def test_multi_broken(self):
        self._broken([0,1,2])
        for i in range(3):
            self._bad_dump(i, 'target is broken')
    
    def test_broken_types(self):
        self._broken((1,2))
        self._broken([1,2])
        self._broken(range(3))
    
    def test_normal_exists(self):
        self._broken([1])
        self._good_exists(0, False)
    
    def test_broken_exists(self):
        self._broken([1])
        self._bad_exists(1, 'target is broken')
    
    def test_broken_load(self):
        self._broken([1])
        self._bad_load(1, 'target is broken')
    
    def _broken(self, li):
        from .bundle import bundle as broken
        from ..memory.bundle import bundle
        self._bundle = broken(bundle(), li)
    
    def _good_dump(self, n, data = b'123'):
        self._dump(n, data)
        self._load(n, data)

    def _dump(self, n, data):
        self._bundle.dump(n, data)
    
    def _load(self, n, expect):
        self.assertEquals(expect, self._bundle.load(n))
        
    def _good_exists(self, n, expect):
        self.assertEquals(expect, self._bundle.exists(n))
    
    def _bad_exists(self, n, message):
        with self._expect_error(message):
            self._bundle.exists(n)
    
    def _bad_broken(self, li, message):
        with self._expect_error(message):
            self._broken(li)
            
    def _bad_load(self, n, message):
        with self._expect_error(message):
            self._bundle.load(n)
            
    def _bad_dump(self, n, message, data = b'123'):
        with self._expect_error(message):
            self._dump(n, data)
    
    def _expect_error(self, message):
        from expecterr.expect_error import expect_error
        return expect_error(message)