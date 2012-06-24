from unittest import TestCase

class test_case(TestCase):
    def setUp(self):
        self._pc_cleanups = []
    
    def tearDown(self):
        for e in self._pc_cleanups:
            e()
    
    def expect(self, v):
        self.assertEquals(v, self.output)
    
    def get_test_file(self, filename):
        import os
        return os.path.join(os.path.dirname(self.script_file), self.test_folder, filename)

    def expect_error(self, error):
        from expecterr.expect_error import expect_error
        return expect_error(error)
    
    def create_temp(self, prefix = ''):
        from tempdir.tempdir import tempdir
        t = tempdir(prefix = prefix)
        self._pc_cleanups.append(lambda:t.__exit__())
        return t.__enter__()