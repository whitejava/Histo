from unittest import TestCase

def _tempdir(prefix = 'extract-rar-test-'):
    from tempdir.tempdir import tempdir
    return tempdir(prefix=prefix)

def _expect_error(error):
    from expecterr.expect_error import expect_error
    return expect_error(error)

def _get_test_file(filename):
    from os.path import join, dirname
    return join(dirname(__file__), '_rar', filename)

class extract_test(TestCase):
    def setUp(self):
        self._temp = _tempdir()
        self._target = self._temp.__enter__()
    
    def tearDown(self):
        self._temp.__exit__(None,None,None)
    
    def test_normal(self):
        self._filename = _get_test_file('normal.rar')
        self._extract()
        self._list()
        self._expect(['/a', '/a/1', '/a/3', '/a/2'])
    
    def test_encrypt(self):
        self._filename = _get_test_file('encrypt.rar')
        self._bad_extract('extract error 1')
    
    def test_bad(self):
        self._filename = _get_test_file('bad.rar')
        self._bad_extract('extract error 10')
    
    def test_nonexist_file(self):
        self._filename = _get_test_file('nonexist.rar')
        self._bad_extract('extract error 10')
    
    def test_command_inject(self):
        self._filename = '\"'
        self._bad_extract('extract error 10')
    
    def test_filename_contain_space(self):
        self._filename = _get_test_file('contain space.rar')
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
    
    def _extract(self):
        from ._extract_archive import extract_archive
        extract_archive('rar', self._filename, self._target)
    
    def _bad_extract(self, error):
        with _expect_error(error):
            self._extract()
        
    def _list(self):
        from listfiles import listfiles
        self._output = listfiles(self._target)
    
    def _expect(self, v):
        self.assertEquals(v, self._output)

class summary_test(TestCase):
    def setUp(self):
        self._name = 'sample'
    
    def test_normal(self):
        self._filename = 'normal.rar'
        self._summary()
        self._expect(('sample', ('rar', None, (('a', (('1', None), ('3', None), ('2', None))),))))
        
    def test_encrypt(self):
        self._filename = 'encrypt.rar'
        self._summary()
        self._expect(('sample', ('rar', 'extract error 1', (('a', ()),))))
    
    def test_bad(self):
        self._filename = 'bad.rar'
        self._summary()
        self._expect(('sample', ('rar', 'extract error 10', ())))
    
    def test_embed(self):
        self._filename = 'embed.rar'
        self._summary()
        self._print_indent()
        self._expect(('sample', ('rar', None, (('embed1.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),)))))), ('embed2.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),)))))), ('embed3.rar', ('rar', None, (('normal.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))), ('normal2.rar', ('rar', None, (('a', (('b', None), ('d', None), ('c', None))),))))))))))
    
    def _summary(self):
        from summary import generate_summary
        self._output = generate_summary(self._name, _get_test_file(self._filename))
    
    def _expect(self, v):
        self.assertEquals(self._output, v)
    
    def _print_output(self):
        print(self._output)
    
    def _print_indent(self):
        from indent import indent
        print(indent(self._output))