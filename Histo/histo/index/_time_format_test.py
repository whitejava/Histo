from unittest import TestCase

def _expect_error(error):
    from expecterr.expect_error import expect_error
    return expect_error(error)

class test(TestCase):
    def test_normal(self):
        self._input = (2012,1,2,3,4,5,123456)
        self._good()
    
    def test_bad(self):
        self._input = (2012,1,2)
        self._bad('input length error')
    
    def test_type_error(self):
        self._input = '123'
        self._bad('input type error')
    
    def _good(self):
        self._check()
    
    def _bad(self, error):
        with _expect_error(error):
            self._check()
    
    def _check(self):
        from . import _time_format
        _time_format.check(self._input)