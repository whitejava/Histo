from unittest import TestCase

class test(TestCase):
    def test_normal(self):
        self._input = '/usr/pc'
        self._good('pc')
    
    def test_single(self):
        self._input = 'abc'
        self._good('abc')
    
    def test_empty(self):
        self._input = ''
        self._good('')
    
    def test_reverse(self):
        self._input = '/usr/pc\\abc'
        self._good('pc\\abc')
    
    def test_no_filename(self):
        self._input = '/usr/pc/'
        self._good('')
    
    def test_bad_filename(self):
        self._input = ':!@#$#!@#$///as/da/fs/d/result'
        self._good('result')
    
    def _good(self, expect):
        self._run()
        self._good_output(expect)
    
    def _run(self):
        from .__init__ import _get_filename
        self._output = _get_filename(self._input)
    
    def _good_output(self, expect):
        self.assertEquals(self._output, expect)