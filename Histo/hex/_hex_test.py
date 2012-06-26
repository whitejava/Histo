from pctest import testcase
from hex import encode, decode

class test(testcase):
    def test_en(self):
        self.batchtest(en, 1, encode, (eval,repr))
    def test_de(self):
        self.batchtest(de, 1, decode, (eval,repr))

en = \
'''
b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
'303132333435363738396162636465666768696a6b6c6d6e6f707172737475767778797a4142434445464748494a4b4c4d4e4f505152535455565758595a'

b''
''

bytearray([1,2,3])
'010203'

'abc'
ValueError("Unknown format code 'x' for object of type 'str'",)

[1,2,3]
'010203'

(1,2,3)
'010203'

[300,400]
'12c190'

None
TypeError("'NoneType' object is not iterable",)
'''

de = \
'''
'616263'
b'abc'

''
b''

'6a'
b'j'

'6A'
b'j'

b'61'
b'a'

'a'
b'\\n'

'000'
b'\\x00\\x00'

'7z'
ValueError("invalid literal for int() with base 16: '7z'",)

'7g'
ValueError("invalid literal for int() with base 16: '7g'",)
'''

'''
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
        self.assertEquals(self._output, value)'''