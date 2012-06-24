from unittest import TestCase

def _tempdir():
    from tempdir.tempdir import tempdir
    return tempdir(prefix='tar-test-')

def _get_test_file(filename):
    import os
    return os.path.join(os.path.dirname(__file__), '_tar', filename)

def _expect_error(error):
    from expecterr.expect_error import expect_error
    return expect_error(error)

class extract_test(TestCase):
    def setUp(self):
        self._temp = _tempdir()
        self._target = self._temp.__enter__()
    
    def tearDown(self):
        self._temp.__exit__()
    
    def test_normal(self):
        self._filename = 'normal.tar'
        self._extract()
        self._list()
        self._expect(['/a', '/a/b', '/a/d', '/a/c'])
    
    def test_bad(self):
        self._filename = 'bad.tar'
        self._bad_extract('tar return error code 2')
    
    def test_bad_target(self):
        import os
        self._filename = 'normal.tar'
        self._target = os.path.join(self._target, 'non-exists')
        self._bad_extract('tar return error code 2')
    
    def _extract(self):
        from summary import _extract_tar
        _extract_tar(_get_test_file(self._filename), self._target)
    
    def _bad_extract(self, error):
        with _expect_error(error):
            self._extract()
    
    def _list(self):
        from listfiles import listfiles
        self._output = listfiles(self._target)
    
    def _expect(self, v):
        self.assertEquals(v, self._output)