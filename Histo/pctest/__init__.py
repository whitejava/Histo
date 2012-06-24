from unittest import TestCase

class test_case(TestCase):   
    def expect(self, v):
        self.assertEquals(v, self._output)
    
    def do(self):
        self._output = self.call()
    
    def get_test_file(self, filename):
        import os
        return os.path.join(os.path.dirname(self.script_file), self.test_folder, filename)
