import unittest
import os
import shutil
from .tempdir import tempdir

class test(unittest.TestCase):
    def test_creation(self):
        with tempdir() as d:
            self.assertTrue(os.path.exists(d))
    
    def test_deletion(self):
        with tempdir() as d:
            pass
        self.assertFalse(os.path.exists(d))
    
    def test_deleted_before_close(self):
        with tempdir() as d:
            shutil.rmtree(d)
    
    def test_undeleteable(self):
        # on linux, this test fails.
        with self.assertRaises(Exception):
            with tempdir() as d:
                f = open(os.path.join(d,'1.txt'),'wb')
        f.close()
        shutil.rmtree(d)