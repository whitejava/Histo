from pctest import testcase as a
from histo.client import _cut as cut

class test(a):
    def test(self):
        self.batchtest(data, 2, cut, (eval, eval, repr))

data = \
'''
'0123456789'
[2,3]
['01', '234']

'0123'
[]
[]

'abc'
[9]
['abc']

'123456789'
[2,100,10]
['12', '3456789', '']

[1,2,3,4,5,6,7]
[2,3,1]
TypeError('initial_value must be str or None, not list',)

b'abc'
[1,2]
TypeError('initial_value must be str or None, not bytes',)

'1234567890'
[0,1,2,3,4]
['', '1', '23', '456', '7890']

None
[1]
['']
'''