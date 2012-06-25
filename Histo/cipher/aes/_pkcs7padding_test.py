from pctest import testcase

class test_encode(testcase):
    def test(self):
        from ._pkcs7padding import encode
        self.batchtest(goodcases, 2, encode, [hex.decode, eval, hex.decode])
        self.batchtest(badcases, 2, self.expecterror(encode), [eval, eval, None])

goodcases = \
'''
aa
1
aa01


2
0202

aa
2
aa01

aabb
2
aabb0202


3
030303

aa
3
aa0202

aabb
3
aabb01

aabbcc
3
aabbcc030303

aabbcc
None
aabbcc0d0d0d0d0d0d0d0d0d0d0d0d0d
'''

badcases = \
'''
b''
0
error

b''
1.1
error

b''
'a'
error

b''
-1
error

b''
-2
error

'a'
3
error

[1]
3
error
'''

class encode_test2(test_case):
    def test_good(self):
        (cases = good_cases,
          paramcount = 2,
          method = encode,
          translate = (hex.decode,
                   eval,
                   hex.decode))

'''

import unittest
from hex.hex import decode

class test(unittest.TestCase):
    def setUp(self):
        self._input = bytes()
        self._size = 3
    
    def test_encode0(self):
        self._expect = decode('030303')
        self._good_encode()
    
    def test_encode1(self):
        self._input = bytes(1)
        self._expect = decode('000202')
        self._good_encode()
    
    def test_encode2(self):
        self._input = bytes(2)
        self._expect = decode('000001')
        self._good_encode()
    
    def test_encode3(self):
        self._input = bytes(3)
        self._expect = decode('000000030303')
        self._good_encode()
    
    def test_decode(self):
        self._input = decode('000202')
        self._expect = decode('00')
        self._good_decode()
    
    def test_decode_empty(self):
        self._bad_decode('decode input is empty')
    
    def test_decode_not_block_size(self):
        self._input = decode('00')
        self._bad_decode('decode input is not padding')
        
    def test_decode_value_error(self):
        self._input = decode('000004040404')
        self._bad_decode('padding value error')

    def test_decode0(self):
        self._input = decode('000000')
        self._bad_decode('padding value error')

    def test_decode1(self):
        self._input = decode('010101')
        self._expect = decode('0101')
        self._good_decode()

    def test_decode2(self):
        self._input = decode('020202')
        self._expect = decode('02')
        self._good_decode()
    
    def test_decode3(self):
        self._input = decode('030303')
        self._expect = decode('')
        self._good_decode()
    
    def test_size_type_error(self):
        self._size = 1.5
        self._bad_encode('size type error')
    
    def test_size_minus(self):
        self._size = -1
        self._bad_encode('size value error')
    
    def test_size_zero(self):
        self._size = 0
        self._bad_encode('size value error')
    
    def test_size_too_big(self):
        self._size = 256
        self._bad_encode('size value error')
    
    def test_encode_type_error(self):
        self._input = list(decode('001122'))
        self._bad_encode('encode input type error')
    
    def test_decode_type_error(self):
        self._input = list(decode('221100'))
        self._bad_decode('decode input type error')
    
    def test_decode_padding_value_error(self):
        self._input = decode('000102')
        self._bad_decode('padding value error')
    
    def _good_encode(self):
        self._encode()
        self._good_output()
    
    def _encode(self):
        self._output = self._pkcs7padding().encode(self._input)
    
    def _good_output(self):
        self.assertEquals(self._expect, self._output)
    
    def _good_decode(self):
        self._decode()
        self._good_output()
    
    def _decode(self):
        self._output = self._pkcs7padding().decode(self._input)

    def _pkcs7padding(self):
        from ._pkcs7padding import padding
        return padding(self._size)

    def _bad_encode(self, message):
        with self._expect_error(message):
            self._encode()

    def _bad_decode(self, message):
        with self._expect_error(message):
            self._decode()
            
    def _expect_error(self, message):
        from expecterr.expect_error import expect_error
        return expect_error(message)'''