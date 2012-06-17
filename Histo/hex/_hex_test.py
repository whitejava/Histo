import unittest

def _expect_error(error):
    from expecterr.expect_error import expect_error
    return expect_error(error)

class test(unittest.TestCase):
    def test_encode_bytes(self):
        self._input = b'abcde'
        self._encode()
        self._expect('6162636465')
    
    def test_encode_other_types(self):
        self._input = bytearray(b'abcde')
        self._bad_encode('input type error')
            
    def test_decode_str(self):
        self._input = '6162636465'
        self._decode()
        self._expect(b'abcde')
        
    def test_decode_other_type(self):
        self._input = list('6162636465')
        self._bad_decode('input type error')
    
    def test_decode_upper_cases(self):
        self._input = 'AABBCC'
        self._decode()
        self._expect(b'\xaa\xbb\xcc')
    
    def test_decode_odd_length(self):
        self._input = '123'
        self._bad_decode('input length odd')
    
    def test_decode_illegal_symbol(self):
        self._input = '7z'
        self._bad_decode('invalid literal for int() with base 16: \'7z\'')
    
    def _encode(self):
        from .hex import encode
        self._output = encode(self._input)
    
    def _bad_encode(self, error):
        with _expect_error(error):
            self._encode()
        
    def _decode(self):
        from .hex import decode
        self._output = decode(self._input)
    
    def _bad_decode(self, error):
        with _expect_error(error):
            self._decode()
    
    def _expect(self, value):
        self.assertEquals(self._output, value)