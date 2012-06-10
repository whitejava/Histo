import unittest
from .repo import repo
from io import BytesIO
from datetime import datetime

class test(unittest.TestCase):
    def test_commit_rar(self):
        index = BytesIO()
        data = BytesIO()
        with repo(index, data) as f:
            f.commit_rar(self._get_normal_rar(), 'Sample', commit_time = datetime(2012,6,10))
        self.assertFile(index, 'normal_index')
        self.assertFile(data, 'normal_data')

    def test_bad_rar(self):
        index = BytesIO()
        data = BytesIO()
        with repo(index, data) as f:
            f.commit_rar(self._get_bad_rar(), 'BadRAR', commit_time = datetime(2012,6,10))
        self.assertFile(index, 'bad_index')
        self.assertFile(data, 'bad_data')

    def test_time(self):
        d = datetime(2012, 6, 10, 1, 20, 38, 13000)
        self.assertEquals(repo._totuple(None,d), (2012, 6, 10, 1, 20, 38, 13000))

    def _get_normal_rar(self):
        return self._get_rar('normal')
    
    def _get_bad_rar(self):
        return self._get_rar('bad')
    
    def _get_rar(self, a):
        return self._get_test_file(a + '.rar')
    
    def _get_test_file(self,f):
        import os
        d = os.path.dirname(__file__)
        return os.path.join(d, '_test_repo', f)
    
    def assertFile(self, bytesio, file):
        file = self._get_test_file(file)
        with open(file,'rb') as f:
            self.assertEquals(bytesio.getvalue(),f.read())