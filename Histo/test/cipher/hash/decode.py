from pctest import testcase
from cipher import hash
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(method, data):
    data = hex.decode(data)
    return hash.cipher(method).decode(data)

data = \
'''
md5
93b885adfe0da089cdf634904fd59f7100
00

sha
c6e20991c4a5ea747fdd7a9e3ce5210504a74e7500
00

sha256
6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d00
00

sha512
b8244d028981d693af7b456af8efa4cad63d282e19ff14942c246e50d9351d22704a802a71c3580b6370de4ceb293c324a8423342557d4e5c38438f0e36910ee00
00
'''