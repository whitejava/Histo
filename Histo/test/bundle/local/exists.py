from pctest import testcase, createfiles
from autotemp import tempdir
from bundle import local

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(creates, id):
    with tempdir() as temp:
        createfiles(temp, creates)
        bundle = local(temp, '{}')
        return bundle.exists(id)

data = \
'''
0:aabb
0
True

0:aabb
1
False

0:<folder>
0
False
'''