from pctest import testcase, createfiles
from autotemp import tempdir
from bundle import local
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(creates, loadid):
    loadid = eval(loadid)
    with tempdir('local-load-test-') as temp:
        createfiles(temp,creates)
        bundle = local(temp,'{}')
        result = bundle.load(loadid)
        result = hex.encode(result)
        return result

data = \
'''
0:aabb
0
aabb

0:aabb
1
IOError(2, 'No such file or directory')

0:<folder>
0
IOError(13, 'Permission denied')
'''