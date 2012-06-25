from pctest import test_case

class test_cut(test_case):
    def test_normal(self):
        self._string = 'abcde'
        self._seg = [2,3]
        self._run()
        self.expect(['ab','cde'])
    
    def _run(self):
        from .client import _cut
        self.output = _cut(self._string, self._seg)
        
class test_resolve_filename(test_case):
    def test_normal(self):
        self._input = '201203071510abc.rar'
        self._run()
        self.expect(((2012,3,7,15,10,0,0),'abc'))
    
    def test_underscore(self):
        self._input = '201207161540_123.rar'
        self._run()
        self.expect(((2012,7,16,15,40,0,0),'123'))
    
    def _run(self):
        from .client import _resolve_filename
        self.output = _resolve_filename(self._input)