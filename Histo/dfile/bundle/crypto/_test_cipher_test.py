import unittest

class test(unittest.TestCase):
    def test_encrypt_empty(self):
        self._good_encrypt(b'', b'ab')
    
    def test_encrypt_content(self):
        self._good_encrypt(b'12', b'a12b')
    
    def test_encrypt_bytearray(self):
        self._bad_encrypt(bytearray(b'123'), 'encrypt input type error')
    
    def test_encrypt_none(self):
        self._bad_encrypt(None, 'encrypt input type error')
        
    def test_decrypt(self):
        self._good_decrypt(b'a123b', b'123')
        
    def test_decrypt_empty(self):
        self._bad_decrypt(b'', 'decrypt input length error')
    
    def test_decrypt_length1(self):
        self._bad_decrypt(b'1', 'decrypt input length error')
    
    def test_decrypt_right_error(self):
        self._bad_decrypt(b'a12', 'decrypt input value error')
    
    def test_decrypt_left_error(self):
        self._bad_decrypt(b'12b', 'decrypt input value error')
    
    def test_decrypt_both_error(self):
        self._bad_decrypt(b'12', 'decrypt input value error')
    
    def test_decrypt_type_error(self):
        self._bad_decrypt([12], 'decrypt input type error')
    
    def test_decrypt_none(self):
        self._bad_decrypt(None, 'decrypt input type error')
    
    def _good_encrypt(self, input, expect):
        cipher = self._get_cipher()
        self.assertEquals(expect, cipher.encrypt(input))
        
    def _bad_encrypt(self, input, error):
        cipher = self._get_cipher()
        with self._expect_error(error):
            cipher.encrypt(input)
    
    def _good_decrypt(self, input, expect):
        cipher = self._get_cipher()
        self.assertEquals(expect, cipher.decrypt(input))
        
    def _bad_decrypt(self, input, error):
        cipher = self._get_cipher()
        with self._expect_error(error):
            cipher.decrypt(input)
    
    def _get_cipher(self):
        from ._test_cipher import cipher
        return cipher()
    
    def _expect_error(self, error):
        from expecterr.expect_error import expect_error
        return expect_error(error)