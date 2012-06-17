import unittest
from .hex import encode
from .hex import decode

class test(unittest.TestCase):
    def test_encode_bytes(self):
        self.assertEquals('6162636465', encode(b'abcde'))
    
    def test_encode_other_types(self):
        with self.assertRaises(TypeError):
            encode(bytearray(b'abcde'))
            
    def test_decode_str(self):
        self.assertEquals(b'abcde', decode('6162636465'))
        
    def test_decode_other_type(self):
        with self.assertRaises(TypeError):
            decode(list('6162636465'))
    
    def test_decode_upper_cases(self):
        self.assertEquals(b'\xaa\xbb\xcc', decode('AABBCC'))
    
    def test_decode_odd_length(self):
        with self.assertRaises(ValueError):
            decode('123')
    
    def test_decode_illegal_symbol(self):
        with self.assertRaises(ValueError):
            decode('7Z')