import unittest
from hex.hex import encode
from hex.hex import decode

class test(unittest.TestCase):
    def setUp(self):
        self._cipher_abc = decode('000100010001000100010001000100014db27f7a76fbdd342e45805492bb42f6')
        self._cipher_abc100 = decode('00010001000100010001000100010001a6ae1eef7c584359a3628c7eb09aae99130d0aeecf0463495146dfdd6385084f0499d45c135612d5bee55f277eaf8f9890bc8f8e35617751928d0bac94baedf88d477051888bbf842e0538722f04126bbdc30cf78f780db6bb123cacb8eecc66c17c54b3538d889341f919e786c4214538b1d0f2648a9d4fb98f7a7cc6f760dbefdc3ca5a4ee82a5fcf245aaba3afdbccb0aec1250c107c4907952ec4df52cd836976ab462e0a38277a7cfc45b3c7e9909794baaa65773f77c2bc5502e1f796fd27f0d1f185135d07f7fadaf7e3e756daeeaabe565f3fbc0431d09c5c62db7c3426a02d8b6732bdc183860eaf63080bfdd231c0f776a70c90811be1d20b22c064765f7fd2823802b2c1ce30491bcff949f5ad02b971d0c6ab669fdbfa25e437be6fd3255f4a4abcafbd3e4ea985f8740')
        self._key1 = decode('000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f')
        self._key2 = decode('0000000000000000000000000000000000000000000000000000000000000000')
        self._abc = b'abc'
        self._abc100 = b'abc' * 100
        self._iv = decode('0001' * 8)
        self._key = self._key1
    
    def test_key_type_error(self):
        self._input = b'abc'
        self._key = []
        self._bad_decrypt('key type error')
    
    def test_encrypt_abc(self):
        self._input = self._abc
        self._expect = self._cipher_abc
        self._good_encrypt()
    
    def test_encrypt_abc100(self):
        self._input = self._abc100
        self._expect = self._cipher_abc100
        self._good_encrypt()
    
    def test_encrypt_with_random_iv(self):
        self._input = self._abc
        self._random_iv()
        self._encrypt()
        self._print_output()
        
    def test_decrypt_abc(self):
        self._input = self._cipher_abc
        self._expect = self._abc
        self._good_decrypt()
    
    def test_decrypt_abc100(self):
        self._input = self._cipher_abc100
        self._expect = self._abc100
        self._good_decrypt()
        
    def test_decrypt_error_too_small(self):
        self._input = decode('0001')
        self._bad_decrypt('decrypt input length error')
    
    def test_bad_padding(self):
        self._input = bytes(32)
        self._bad_decrypt('padding value error')
    
    def test_encrypt_invalid_key(self):
        self._key = b'1234'
        self._input = b''
        self._bad_decrypt('key length error')
        
    def test_decrypt_wrong_key(self):
        self._input = b'1234'
        self._random_iv()
        self._encrypt()
        self._key = self._key2
        self._input = self._output
        self._bad_decrypt('padding value error')
    
    def test_decrypt_type_error(self):
        self._input = []
        self._bad_decrypt('decrypt input type error')
    
    def test_decrypt_not_block_size(self):
        self._input = b'1' * 20
        self._bad_decrypt('decrypt input length error')
    
    def test_decrypt_encrypt_diffrent_lengths(self):
        self._random_iv()
        for i in range(20):
            self._decrypt_encrypt(bytes(i))
    
    def _decrypt_encrypt(self, text):
        self._input = text
        self._encrypt()
        self._print_output()
        self._input = self._output
        self._expect = text
        self._good_decrypt()
    
    def _good_encrypt(self):
        self._encrypt()
        self._good_output()
    
    def _encrypt(self):
        from .cipher import cipher
        c = cipher(self._key)
        if self._iv:
            self._output = c._encrypt_wrap_iv(self._input, self._iv)
        else:
            self._output = c.encrypt(self._input)

    def _good_decrypt(self):
        self._decrypt()
        self._good_output()
    
    def _decrypt(self):
        from .cipher import cipher
        self._output = cipher(self._key).decrypt(self._input)
    
    def _good_output(self):
        self.assertEquals(self._expect, self._output)
    
    def _random_iv(self):
        self._iv = None
    
    def _print_output(self):
        print(encode(self._output))
    
    def _bad_encrypt(self, message):
        try:
            self._encrypt()
        except Exception as e:
            self.assertEquals(e.args[0], message)
        else:
            self.fail('expect encrypt error')
    
    def _bad_decrypt(self, message):
        try:
            self._decrypt()
        except Exception as e:
            self.assertEquals(e.args[0], message)
        else:
            self.fail('expect decrypt error')