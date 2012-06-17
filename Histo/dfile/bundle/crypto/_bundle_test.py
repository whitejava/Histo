from unittest import TestCase

class test(TestCase):
    def setUp(self):
        self._input = b''
        self._id = 0
        self._cipher = self._get_cipher()
        self._bundle = self._get_memory_bundle()
        self._crypto = self._get_crypto_bundle()
    
    def test_dump(self):
        self._input = b'12345'
        self._expect = b'a12345b'
        self._dump()
        self._good_load_base()
    
    def test_load(self):
        self._input = b'a12345b'
        self._expect = b'12345'
        self._dump_base()
        self._good_load()
    
    def test_mix(self):
        for _ in range(10):
            for i in range(10):
                self._id = i
                self._input = b'1' * i
                self._expect = self._input
                self._dump()
                self._good_load()
                
    def test_decrypt_error(self):
        self._input = b'12345'
        self._error = 'decrypt input value error'
        self._dump_base()
        self._bad_load()
    
    def test_dump_id_type(self):
        self._id = 1.5
        self._dump()
    
    def test_dump_data_type_error(self):
        self._input = [123]
        self._error = 'dump data type error'
        self._bad_dump()
    
    def test_load_id_type(self):
        self._id = 1.5
        self._dump()
        self._load()
    
    def _dump(self):
        self._crypto.dump(self._id, self._input)
    
    def _good_load_base(self):
        self._load_base()
        self._good_output()
    
    def _dump_base(self):
        self._bundle.dump(self._id, self._input)
    
    def _good_load(self):
        self._load()
        self._good_output()
    
    def _bad_load(self):
        with self._expect_error():
            self._load()
        
    def _bad_dump(self):
        with self._expect_error():
            self._dump()
    
    def _good_output(self):
        self.assertEquals(self._expect, self._output)
    
    def _load(self):
        self._output = self._crypto.load(self._id)
    
    def _load_base(self):
        self._output = self._bundle.load(self._id)
    
    def _get_memory_bundle(self):
        from ..memory.bundle import bundle
        return bundle()
    
    def _get_crypto_bundle(self):
        from .bundle import bundle
        return bundle(self._bundle, self._cipher)
    
    def _get_cipher(self):
        from ._test_cipher import cipher
        return cipher()
    
    def _expect_error(self):
        from expecterr.expect_error import expect_error
        return expect_error(self._error)