from unittest import TestCase

class test(TestCase):
    def setUp(self):
        self._id = 0
        self._input = b'123'
        self._bundle = self._get_bundle()
    
    def test_dump(self):
        self._dump()
    
    def test_load(self):
        self._expect = self._input
        self._dump()
        self._good_load()
    
    def test_load_not_exists(self):
        self._error = "'id not exists'"
        self._bad_load()
    
    def test_not_exists(self):
        self._expect = False
        self._good_exists()
    
    def test_exists(self):
        self._expect = True
        self._dump()
        self._good_exists()
    
    def test_delete(self):
        self._expect = False
        self._dump()
        self._delete()
        self._good_exists()
    
    def test_id_type(self):
        self._id = 1.6
        self._dump()
    
    def test_data_type(self):
        self._input = {1.5:23}
        self._dump()
    
    def test_delete_not_exists(self):
        self._error = "'id not exists'"
        self._bad_delete()
    
    def test_dump_overwrite(self):
        self._input = b'123'
        self._dump()
        self._input = b'abc'
        self._dump()
        self._expect = self._input
        self._good_load()
    
    def _get_bundle(self):
        from .bundle import bundle
        return bundle()
    
    def _dump(self):
        self._bundle.dump(self._id, self._input)
    
    def _good_load(self):
        self._load()
        self._good_output()
    
    def _bad_load(self):
        with self._expect_error():
            self._load()
    
    def _load(self):
        self._output = self._bundle.load(self._id)
        
    def _delete(self):
        self._bundle.delete(self._id)
        
    def _good_exists(self):
        self._exists()
        self._good_output()
    
    def _bad_exists(self):
        with self._expect_error():
            self._exists()
    
    def _good_output(self):
        self.assertEquals(self._expect, self._output)
    
    def _expect_error(self):
        from expecterr.expect_error import expect_error
        return expect_error(self._error)
    
    def _exists(self):
        self._output = self._bundle.exists(self._id)
    
    def _bad_delete(self):
        with self._expect_error():
            self._delete()