import unittest

from bundle import bundle

class test(unittest.TestCase):
    def test_dump(self):
        lib = bundle()
        lib.dump(0,b'123')
    
    def test_load(self):
        lib = bundle()
        lib.dump(0,b'123')
        assert lib.load(0) == b'123'
    
    def test_load_not_exist(self):
        lib = bundle()
        with self.assertRaises(KeyError):
            lib.load(1)

if __name__ == "__main__":
    unittest.main()
