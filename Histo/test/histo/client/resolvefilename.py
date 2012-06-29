from pctest import testcase, gettestfile
from histo.client import _resolvefilename as resolvefilename

class test(testcase):
    def test(self):
        self.batchtest(data, 1, resolvefilename, (eval, repr))

data = \
'''
'201206262245normal.rar'
((2012, 6, 26, 22, 45, 0, 0), 'normal')

'201206262245_123digit.rar'
((2012, 6, 26, 22, 45, 0, 0), '123digit')

'201206262245.rar'
((2012, 6, 26, 22, 45, 0, 0), '')

'201206262245.tar.gz'
((2012, 6, 26, 22, 45, 0, 0), '.ta')

'123'
ValueError("invalid literal for int() with base 10: ''",)

123
AttributeError("'int' object has no attribute 'rfind'",)

None
AttributeError("'NoneType' object has no attribute 'rfind'",)

b'201206262245.tar.gz'
TypeError('initial_value must be str or None, not bytes',)
'''