from unittest import TestCase

def _tempdir(prefix = 'extract-test-'):
    from tempdir.tempdir import tempdir
    return tempdir(prefix=prefix)

def _expect_error(error):
    from expecterr.expect_error import expect_error
    return expect_error(error)

def _get_test_file(filename):
    from os.path import join, dirname
    return join(dirname(__file__), '_archive', filename)

class test_common(TestCase):
    def setUp(self):
        self._temp = _tempdir()
        self._target = self._temp.__enter__()

    def tearDown(self):
        self._temp.__exit__(None,None,None)
    
    def _extract(self):
        from ._extract_archive import extract_archive
        extract_archive(self._type, _get_test_file(self._filename), self._target)
    
    def _bad_extract(self, error):
        with _expect_error(error):
            self._extract()
        
    def _list(self):
        from listfiles import listfiles
        self._output = listfiles(self._target)
    
    def _expect(self, v):
        self.assertEquals(v, self._output)

class rar_test(test_common):
    def setUp(self):
        test_common.setUp(self)
        self._type = 'rar'

    def test_normal(self):
        self._filename = 'normal.rar'
        self._extract()
        self._list()
        self._expect(['/a', '/a/1', '/a/3', '/a/2'])
    
    def test_encrypt(self):
        self._filename = 'encrypt.rar'
        self._bad_extract('extract error 1')
    
    def test_bad(self):
        self._filename = 'bad.rar'
        self._bad_extract('extract error 10')
    
    def test_nonexist_file(self):
        self._filename = 'nonexist.rar'
        self._bad_extract('extract error 10')
    
    def test_command_inject(self):
        self._filename = '\"'
        self._bad_extract('extract error 10')
    
    def test_filename_contain_space(self):
        self._filename = 'contain space.rar'
        self._extract()
        self._list()
        self._expect(['/a', '/a/1', '/a/3', '/a/2'])
    
    def test_target_contain_space(self):
        with _tempdir('target contain space') as temp:
            self._filename = _get_test_file('normal.rar')
            self._target = temp
            self._extract()
            self._list()
            self._expect(['/a', '/a/1', '/a/3', '/a/2'])
    
    def test_bad_target(self):
        import os
        self._filename = _get_test_file('normal.rar')
        self._target = os.path.join(self._target, 'not-exist')
        self._extract()
        self._list()
        self._expect(['/a', '/a/1', '/a/3', '/a/2'])

class tar_test(test_common):
    def setUp(self):
        test_common.setUp(self)
        self._type = 'tar'
    
    def test_normal(self):
        self._filename = 'normal.tar'
        self._extract()
        self._list()
        self._expect(['/a', '/a/b', '/a/d', '/a/c'])
    
    def test_bad(self):
        self._filename = 'bad.tar'
        self._bad_extract('extract error 2')
    
    def test_bad_target(self):
        import os
        self._filename = 'normal.tar'
        self._target = os.path.join(self._target, 'non-exist')
        self._bad_extract('extract error 2')
    
    def test_bz2(self):
        self._filename = 'normal.tar.bz2'
        self._extract()
        self._list()
        self._expect(['/a', '/a/b', '/a/d', '/a/c'])
    
    def test_gz(self):
        self._filename = 'normal.tar.gz'
        self._extract()
        self._list()
        self._expect(['/a', '/a/1', '/a/3', '/a/2'])

class zip_test(test_common):
    def setUp(self):
        test_common.setUp(self)
        self._type = 'zip'
    
    def test_normal(self):
        self._filename = 'normal.zip'
        self._extract()
        self._list()
        self._expect(['/a', '/a/b', '/a/d', '/a/c'])
    
    def test_bad(self):
        self._filename = 'bad.zip'
        self._bad_extract('extract error 9')
    
    def test_bad_target(self):
        import os
        self._filename = 'normal.zip'
        self._target = os.path.join(self._target, 'non-exist')
        self._extract()
        self._list()
        self._expect(['/a', '/a/b', '/a/d', '/a/c'])
    
    def test_encrypt(self):
        self._filename = 'encrypt.zip'
        self._bad_extract('extract error 5')