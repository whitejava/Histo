import unittest
from .cipher import cipher
from ..decrypt_error import decrypt_error
from .bad_padding_error import bad_padding_error

def tobytes(a):
    return bytes([int(a[i:i+2],16)for i in range(0,len(a),2)])

def tohex(b):
    return ''.join(['{:02x}'.format(e) for e in b])

class test(unittest.TestCase):
    _cipher_abc = tobytes('000100010001000100010001000100014db27f7a76fbdd342e45805492bb42f6')
    _cipher_abc100 = tobytes('00010001000100010001000100010001a6ae1eef7c584359a3628c7eb09aae99130d0aeecf0463495146dfdd6385084f0499d45c135612d5bee55f277eaf8f9890bc8f8e35617751928d0bac94baedf88d477051888bbf842e0538722f04126bbdc30cf78f780db6bb123cacb8eecc66c17c54b3538d889341f919e786c4214538b1d0f2648a9d4fb98f7a7cc6f760dbefdc3ca5a4ee82a5fcf245aaba3afdbccb0aec1250c107c4907952ec4df52cd836976ab462e0a38277a7cfc45b3c7e9909794baaa65773f77c2bc5502e1f796fd27f0d1f185135d07f7fadaf7e3e756daeeaabe565f3fbc0431d09c5c62db7c3426a02d8b6732bdc183860eaf63080bfdd231c0f776a70c90811be1d20b22c064765f7fd2823802b2c1ce30491bcff949f5ad02b971d0c6ab669fdbfa25e437be6fd3255f4a4abcafbd3e4ea985f8740')
    
    def setUp(self):
        self.key = tobytes('000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f')
        self.key2 = b'1' * 32
    
    def test_encrypt(self):
        c = cipher(self.key)
        iv = tobytes('0001'*8)
        actual_abc = c._encrypt_wrap_iv(b'abc',iv)
        actual_abc100 = c._encrypt_wrap_iv(b'abc'*100,iv)
        print(tohex(actual_abc))
        print(tohex(actual_abc100))
        self.assertEquals(actual_abc, self._cipher_abc)
        self.assertEquals(actual_abc100, self._cipher_abc100)
    
    def test_encrypt_with_random_iv(self):
        c = cipher(self.key)
        code = c.encrypt(b'abc')
        print(tohex(code))
    
    def test_encrypt_decrypt_with_wide_range_of_length(self):
        for i in range(20):
            c = cipher(self.key)
            text = b'a' * i
            encrypt = c.encrypt(text)
            decrypt = c.decrypt(encrypt)
            self.assertEquals(text, decrypt)
    
    def test_decrypt(self):
        c = cipher(self.key)
        code1 = self._cipher_abc
        code2 = self._cipher_abc100
        print(tohex(c.decrypt(code1)))
        print(tohex(c.decrypt(code2)))
        assert c.decrypt(code1) == b'abc'
        assert c.decrypt(code2) == b'abc'*100
    
    def test_decrypt_error_too_small(self):
        c = cipher(self.key)
        code1 = tobytes('0001')
        with self.assertRaises(decrypt_error):
            c.decrypt(code1)
    
    def test_decrypt_error_bad_padding(self):
        c = cipher(self.key)
        code = tobytes('00'*16)
        with self.assertRaises(bad_padding_error):
            c.decrypt(code)
    
    def test_invalid_key(self):
        with self.assertRaises(Exception):
            cipher(b'1234')
    
    def test_decrypt_wrong_key(self):
        c = cipher(self.key)
        code = c.encrypt(b'1234')
        c2 = cipher(self.key2)
        with self.assertRaises(bad_padding_error):
            c2.decrypt(code)
            
    def test_invalid_iv(self):
        c = cipher(self.key)
        with self.assertRaises(Exception):
            c.encrypt(b'12345',iv=b'a')
    
    def test_decrypt_not_block_size(self):
        c = cipher(self.key)
        with self.assertRaises(Exception):
            c.decrypt(b'132131232131232131321312')

    def test_padding(self):
        c = cipher(self.key)
        p = c._padding(tobytes('00'*11))
        self.assertEquals(p, tobytes('00'*11 + '05'*5))
        self.assertEquals(c._padding(tobytes('00'*16)), tobytes('00'*16+'10'*16))
    
    def test_unpadding(self):
        c = cipher(self.key)
        t = c._unpadding(tobytes('00'*11 + '05'*5))
        self.assertEquals(t, tobytes('00'*11))
        
    def test_bad_padding(self):
        c = cipher(self.key)
        with self.assertRaises(bad_padding_error):
            c._unpadding(tobytes('00'*16))
            
    def test_empty_bad_padding(self):
        c = cipher(self.key)
        with self.assertRaises(bad_padding_error):
            c._unpadding(b'')