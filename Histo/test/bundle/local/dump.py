from autotemp import tempdir
from pctest import testcase,dumpdir
from bundle import local
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(format,*writes):
    with tempdir('local-test-') as temp:
        writes = [e.split(':') for e in writes]
        bundle = local(temp,format)
        for id,data in writes:
            id = eval(id)
            data = hex.decode(data)
            bundle.dump(id,data)
        return dumpdir(temp)

data = \
'''
{:04}
0:aabb
0000:aabb

{:04}
0:aabb
0:ccdd
0000:ccdd

{:04}
0:aabb
1:ccdd
0000:aabb,0001:ccdd
'''