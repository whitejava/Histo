import unittest

from library import library

class test(unittest.TestCase):
    def test_dump(self):
        lib = library()
        lib.dump(0,b'123')
    
    def test_load(self):
        lib = library()
        lib.dump(0,b'123')
        assert lib.load(0) == b'123'
    
    def test_load_not_exist(self):
        lib = library()
        with self.assertRaises(KeyError):
            lib.load(1)

if __name__ == "__main__":
    unittest.main()