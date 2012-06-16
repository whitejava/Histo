import unittest

def _expect_error(error):
    from expecterr.expect_error import expect_error
    return expect_error(error)

class test(unittest.TestCase):
    def setUp(self):
        from ._test_common import common
        self._sample = list(common().sample)
    
    def test_normal(self):
        self._good()
    
    def test_version_normal(self):
        self._set_version(0)
        self._good()
    
    def test_version_newer(self):
        self._set_version(1)
        self._bad('version error')
    
    def test_version_older(self):
        self._set_version(-1)
        self._bad('version error')
    
    def test_time_normal(self):
        self._set_time((2012,1,1,0,0,0,123456))
        self._good()
    
    def test_time_only_year(self):
        self._set_time((2012,))
        self._bad('time length error')
    
    def test_time_year_month(self):
        self._set_time((2012,6))
        self._bad('time length error')
    
    def test_time_year_month_day(self):
        self._set_time((2012,6,12))
        self._bad('time length error')
    
    def test_time_year_month_day_hour(self):
        self._set_time((2012,6,12,13))
        self._bad('time length error')
    
    def test_time_year_month_day_hour_minute(self):
        self._set_time((2012,6,12,13,14))
        self._bad('time length error')
    
    def test_time_year_month_day_hour_minute_second(self):
        self._set_time((2012,6,12,13,14,15))
        self._bad('time length error')
        
    def test_time_month_exceed(self):
        self._set_time((2012,13,1,12,20,13))
        self._good()
    
    def test_time_day_exceed(self):
        self._set_time((2012,1,32,1,1,1,1))
        self._good()
    
    def test_time_type_error(self):
        self._set_time([1,2,3])
        self._bad('time type error')
    
    def test_time_item_type_error(self):
        self._set_time((2012,1,1,1,1,1,1.123))
        self._bad('time item type error')
    
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
        self._bad('last modify type error')
    
    def test_last_modify_length_error(self):
        self._set_last_modify((2012,1))
        self._bad('last modify length error')
    
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
        self._bad('range value reverse')
    
    def test_summary_normal(self):
        self._set_summary('text')
        self._good()
    
    def test_summary_type_error(self):
        self._set_summary(None)
        self._bad('summary type error')
    
    def test_item_error(self):
        self._sample[0] = ('version', 1, 2)
        self._bad('item length error')
    
    def test_item_name_error(self):
        self._sample[0] = ('unknown', 1)
        self._bad('item name error')
    
    def test_disorder(self):
        a = self._sample
        a[2],a[3] = a[3],a[2]
        self._bad('item name error')
    
    def test_more_item(self):
        self._sample.append(('more', 0))
        self._bad('input length error')
    
    def test_less_item(self):
        del self._sample[-1]
        self._bad('input length error')
    
    def test_type_error(self):
        self.s = dict(self.s)
        self._bad('input type error')
    
    def _set_version(self, version):
        self._sample[0] = ('version', version)
    
    def _set_time(self, time):
        self._sample[1] = ('time', time)
    
    def _set_name(self, name):
        self._sample[2] = ('name', name)
    
    def _set_last_modify(self, v):
        self._sample[3] = ('last-modify', v)
    
    def _set_summary(self, v):
        self._sample[4] = ('summary', v)
    
    def _good(self):
        self._check()
    
    def _bad(self, error):
        with _expect_error(error):
            self._check()
    
    def _check(self):
        from ._format import format
        format().check(self._sample)