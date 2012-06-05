import unittest
from unittest import TestCase
from reader import reader
from files.memory.memory_files import memory_files as files

class test(TestCase):
    def __init__(self,a):
        TestCase.__init__(self,a)
    
    def test_read(self):
        fs = files()
        fs.open_for_write(0)