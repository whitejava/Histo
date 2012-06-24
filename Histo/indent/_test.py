from unittest import TestCase

result0 =\
'''(
    1,
    (
    ),
    'asdf',
    (
        'a',
        'b',
    ),
    (
        2,
        3,
    ),
    (
        4,
        (
            5,
            6,
            7,
        ),
    ),
)'''

class test(TestCase):
    def test(self):
        self._input = (1, (), 'asdf', ['a','b'], (2,3),(4,(5,6,7)))
        self._indent()
        self._print_output()
        self._expect(result0)
    
    def _indent(self):
        from indent import indent
        self._output = indent(self._input)
    
    def _expect(self, v):
        self.assertEquals(v, self._output)
    
    def _print_output(self):
        print(self._output)