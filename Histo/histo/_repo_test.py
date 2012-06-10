import unittest
from .repo import repo
from io import BytesIO

class test(unittest.TestCase):
    def test_commit_rar(self):
        index = BytesIO()
        data = BytesIO()
        with repo(index, data) as f:
            f.commit_rar(self._get_normal_rar(), commit_time = (2012,6,10))
        self.assertFile(index, '_normal_index')
        self.assertFile(data, '_normal_data')

    def test_bad_rar(self):
        index = BytesIO()
        data = BytesIO()
        with repo(index, data) as f:
            f.commit_rar(self._get_bad_rar(), commit_time = (2012,6,10))
        self.assertFile(index, '_bad_index')
        self.assertFile(data, '_bad_data')

    def test_time(self):
        import datetime
        d = datetime.datetime(2012, 6, 10, 1, 20, 38, 13000)
        self.assertEquals(repo._totuple(d), (2012, 6, 10, 1, 20, 38, 13000))

    def _get_normal_rar(self):
        return self._get_rar('_normal')
    
    def _get_rar(self, a):
        import os
        d = os.path.dirname(__file__)
        return os.path.join(d, '_' + a +'.rar')
    
    def assertFile(self, bytesio, file):
        with open(file,'rb') as f:
            self.assertEquals(bytesio.getvalue(),f.read())