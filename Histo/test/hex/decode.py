from pctest import testcase
import hex

class test(testcase):
    def test(self):
        self.batchtest(data, 1, hex.decode, (eval, repr))

data = \
'''
'616263'
b'abc'

''
b''

'6a'
b'j'

'6A'
b'j'

b'61'
b'a'

'a'
b'\\n'

'000'
b'\\x00\\x00'

'7z'
ValueError("invalid literal for int() with base 16: '7z'",)

'7g'
ValueError("invalid literal for int() with base 16: '7g'",)
'''