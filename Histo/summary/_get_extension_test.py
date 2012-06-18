from unittest import TestCase

class test(TestCase):
    def test_normal(self):
        self._input = '/usr/pc/1.rar'
        self._good('rar')
    
    def test_just_extension(self):
        self._input = '.rar'
        self._good('rar')
    
    def test_no_extension(self):
        self._input = 'no-extension'
        self._good(None)
    
    def test_folder_extension(self):
        import platform
        system = platform.system()
        if system == 'Linux':
            self._input = '/usr/pc.folder/text'
            self._good(None)
        else:
            self.fail('unknown os')
    
    def test_empty_extension(self):
        self._input = '123.'
        self._good('')
    
    def test_case_extension(self):
        self._input = '123.aBc'
        self._good('aBc')
    
    def test_multidot(self):
        self._input = 'abc.def.rar.txt.jar'
        self._good('jar')
    
    def _good(self, expect):
        self._run()
        self._good_output(expect)
    
    def _run(self):
        from .__init__ import _get_extension
        self._output = _get_extension(self._input)
    
    def _good_output(self, expect):
        self.assertEquals(self._output, expect)