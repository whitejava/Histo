from pctest import test_case

class test(test_case):
    def setUp(self):
        from .bundle import bundle
        test_case.setUp(self)
        self._id = 0
        self._input = b'1234'
        self._bundle = bundle(self.create_temp(), '{:04d}')
    
    def test_dump(self):
        self._dump()
        
    def test_load(self):
        self._dump()
        self._load()
        self.expect(self._input)
    
    def test_overwrite(self):
        self._dump()
        self._input = b'345'
        self._dump()
        self._load()
        self.expect(b'345')
    
    def test_not_exists(self):
        self._exists()
        self.expect(False)
    
    def test_exists(self):
        self._dump()
        self._exists()
        self.expect(True)
    
    def test_load_not_exist(self):
        with self.expect_error("'id not exists'"):
            self._load()
    
    def _dump(self):
        self._bundle.dump(self._id, self._input)
    
    def _load(self):
        self.output = self._bundle.load(self._id)
    
    def _exists(self):
        self.output = self._bundle.exists(self._id)