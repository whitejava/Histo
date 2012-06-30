from pctest import testcase
from cipher.aes import cipher
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(key, data):
    key = eval(key)
    data = eval(data)
    c = cipher(key)
    code = c.encode(data)
    print(hex.encode(code))
    result = c.decode(code)
    return '{},{}'.format(len(code),repr(result))

data = \
'''
b'1'*32
b''
32,b''

b'1'*32
b'a'
32,b'a'

b'1'*32
b'abc'
32,b'abc'

b'1'*32
b'0123456789abcdef'
48,b'0123456789abcdef'

b'1'*24
b'0123'
32,b'0123'

b'1'*16
b'abc'
32,b'abc'

'1'*32
b'abc'
32,b'abc'

'1'*24
b'abc'
32,b'abc'

'1'*16
b'abc'
32,b'abc'
'''