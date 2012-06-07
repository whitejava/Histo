import unittest
from ._test_cipher import test_cipher as cipher
from ._decrypt_error import decrypt_error

class test(unittest.TestCase):
    def test_encrypt(self):
        c = cipher()
        assert c.encrypt(b'') == b'ab'
        assert c.encrypt(b'12') == b'a12b'
        assert c.encrypt(bytearray(b'123')) == b'a123b'
    
    def test_decrypt(self):
        c = cipher()
        assert c.decrypt(b'ab') == b''
        assert c.decrypt(b'a12b') == b'12'
        assert c.decrypt(bytearray(b'a123b')) == b'123'
    
    def test_decrypt_error(self):
        c = cipher()
        with self.assertRaises(decrypt_error):
            c.decrypt(b'a1')
        with self.assertRaises(decrypt_error):
            c.decrypt(b'1b')
        with self.assertRaises(decrypt_error):
            c.decrypt(b'12')
        with self.assertRaises(decrypt_error):
            c.decrypt(b'')