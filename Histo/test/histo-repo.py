import unittest

def _expect_error(error):
    from expecterr.expect_error import expect_error
    return expect_error(error)

def _get_test_dir():
    from os.path import join, dirname
    return join(dirname(__file__), '_test_repo')

def _get_test_file(filename):
    from os.path import join
    return join(_get_test_dir(), filename)

class test(unittest.TestCase):
    def setUp(self):
        from io import BytesIO
        self._index_output = BytesIO()
        self._data_output = BytesIO()
        self._filename = _get_test_file('normal.rar')
        self._name = 'normal'
        self._time = (2012, 6, 17, 13, 28, 19, 123456)
        self._summary = 'summary'
    
    def test_normal(self):
        self._good('normal')

    def test_time_now(self):
        self._set_time(None)
        self._good()
        self._print_output()

    def _good(self, prefix = None):
        self._commit()
        if prefix is not None:
            self._assert_test_file_equals(prefix + '_index', self._index_output)
            self._assert_test_file_equals(prefix + '_data', self._data_output)
    
    def _set_filename(self, v):
        self._filename = v
    
    def _set_name(self, v):
        self._name = v
        
    def _set_time(self, v):
        self._time = v
    
    def _bad(self, error):
        with _expect_error(error):
            self._commit()
    
    def _dump(self, name):
        with open(_get_test_file(name + '_index'), 'wb') as f:
            f.write(self._index_output.getvalue())
        with open(_get_test_file(name + '_data'), 'wb') as f:
            f.write(self._data_output.getvalue())
    
    def _print_output(self):
        print(self._index_output.getvalue())
        print(self._data_output.getvalue())
    
    def _commit(self):
        from .repo import repo
        repo(self._index_output, self._data_output).commit_file(self._filename, self._name, self._summary, self._time)
    
    def _assert_test_file_equals(self, filename, bytesio):
        self._assert_file_equals(_get_test_file(filename), bytesio)
    
    def _assert_file_equals(self, filename, bytesio):
        with open(filename, 'rb') as f:
            self.assertEquals(f.read(), bytesio.getvalue())