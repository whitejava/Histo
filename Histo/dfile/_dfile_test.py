from files.memory_files import memory_files
from _data_generator import data_generator
from unittest import TestCase
from random import randint
from dfile import reader
from dfile import writer
import unittest

class dfile_test(TestCase):
    def test_memory_reader(self):
        files = self._create_sample_files()
        with self._create_reader(files, 10) as f:
            self._read_bulk_data(f)
            self._read_random_access(f)
    
    def test_memory_writer(self):
        with self._create_memory_writer(10) as f:
            self._write_bulk_data(f)
    
    def _write_bulk_data(self,f):
        d = data_generator()
        for _ in range(1000):
            length = self._random_length()
            f.write(d.read(length))
    
    def _read_bulk_data(self,f):
        d = data_generator()
        while True:
            length = self._random_length()
            actual = f.read(length)
            expect = d.read(len(actual))
            if length and not actual:
                break
            assert actual == expect
    
    def _read_random_access(self,f):
        d = data_generator()
        for _ in range(1000):
            ra = self._random_range(f.get_file_size())
            actual = self._read_range(f, ra)
            expect = self._read_range(d, ra)
            assert actual == expect
            
    def _create_sample_files(self):
        r = self._create_memory_files()
        with self._create_writer(r) as f:
            self._write_bulk_data(f)
        return r
    
    def _read_range(self, file, ra):
        file.seek(ra[0])
        return file.read(len(ra))
    
    def _random_length(self):
        return randint(0,40)
    
    def _create_memory_writer(self, part_size):
        return self._create_writer(self._create_memory_files(), part_size)
    
    def _create_memory_files(self):
        return memory_files()
    
    def _create_writer(self, files, part_size):
        return writer(files, part_size)
    
    def _create_reader(self, files, part_size):
        return reader(files, part_size)

unittest.main()