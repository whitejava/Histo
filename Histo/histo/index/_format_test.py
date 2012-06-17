import unittest

def _expect_error(error):
    from expecterr.expect_error import expect_error
    return expect_error(error)

class test(unittest.TestCase):
    def setUp(self):
        from ._test_common import common
        self._input = list(common().sample)
        self._convert_tuple = True
    
    def test_normal(self):
        self._good()
    
    def test_version_normal(self):
        self._set_version(0)
        self._good()
    
    def test_version_newer(self):
        self._set_version(1)
        self._bad('version value error')
    
    def test_version_older(self):
        self._set_version(-1)
        self._bad('version value error')
    
    def test_time_normal(self):
        self._set_time((2012,1,1,0,0,0,123456))
        self._good()
    
    def test_time_bad(self):
        self._set_time((2012,1,1))
        self._bad('input length error')
        
    def test_time_month_exceed(self):
        self._set_time((2012,13,1,12,20,13,12345))
        self._good()
    
    def test_time_day_exceed(self):
        self._set_time((2012,1,32,1,1,1,1))
        self._good()
    
    def test_time_type_error(self):
        self._set_time([1,2,3])
        self._bad('input type error')
    
    def test_time_item_type_error(self):
        self._set_time((2012,1,1,1,1,1,1.123))
        self._bad('item type error')
    
    def test_name_type_error(self):
        self._set_name(None)
        self._bad('name type error')
    
    def test_name_normal(self):
        self._set_name('abc')
        self._good()
    
    def test_name_empty(self):
        self._set_name('')
        self._good()
    
    def test_last_modify_normal(self):
        self._set_last_modify((2012,1,1,1,1,1,123456))
        self._good()
    
    def test_last_modify_type_error(self):
        self._set_last_modify(None)
        self._bad('input type error')
    
    def test_last_modify_length_error(self):
        self._set_last_modify((2012,1))
        self._bad('input length error')
    
    def test_range_normal(self):
        self._set_range((0,2))
        self._good()
    
    def test_range_minus(self):
        self._set_range((-1, 10))
        self._bad('range value minus')
    
    def test_range_empty(self):
        self._set_range((10,10))
        self._good()
    
    def test_range_reverse(self):
        self._set_range((10,9))
        self._bad('range value error')
    
    def test_summary_normal(self):
        self._set_summary('text')
        self._good()
    
    def test_summary_type_error(self):
        self._set_summary(None)
        self._bad('summary type error')
    
    def test_item_error(self):
        self._input[0] = ('version', 1, 2)
        self._bad('item length error')
    
    def test_item_name_error(self):
        self._input[0] = ('unknown', 1)
        self._bad('item name error')
    
    def test_disorder(self):
        a = self._input
        a[2],a[3] = a[3],a[2]
        self._bad('item name error')
    
    def test_more_item(self):
        self._input.append(('more', 0))
        self._bad('input length error')
    
    def test_less_item(self):
        del self._input[-1]
        self._bad('input length error')
    
    def test_type_error(self):
        self._input = dict(self._input)
        self._set_no_convert_tuple()
        self._bad('input type error')
    
    def _set_version(self, version):
        self._input[0] = ('version', version)
    
    def _set_time(self, time):
        self._input[1] = ('time', time)
    
    def _set_name(self, name):
        self._input[2] = ('name', name)
    
    def _set_last_modify(self, v):
        self._input[3] = ('last-modify', v)
    
    def _set_range(self, v):
        self._input[4] = ('range', v)
    
    def _set_summary(self, v):
        self._input[5] = ('summary', v)
    
    def _set_no_convert_tuple(self):
        self._convert_tuple = False
    
    def _good(self):
        self._check()
    
    def _bad(self, error):
        with _expect_error(error):
            self._check()

    def _check(self):
        if self._convert_tuple:
            self._input = tuple(self._input)
        from . import _format
        _format.check(self._input)