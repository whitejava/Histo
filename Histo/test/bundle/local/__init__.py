from pctest import testcase,dumpdir
from bundle import local
from autotemp import tempdir
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(*script):
    with tempdir() as temp:
        bundle = local(temp, '{:04}')
        t = {'dump':lambda x,y:bundle.dump(eval(x),hex.decode(y)),
             'load':lambda x:bundle.load(eval(x)),
             'exists':lambda x:bundle.exists(eval(x)),
             'dumpdir':lambda:dumpdir(temp)}
        result = []
        for ins in script:
            ins = ins.split(' ')
            command = ins[0]
            command = t[command]
            params = ins[1:]
            result.append(repr(command(*params)))
        return '-'.join(result)

data = \
'''
dump 0 aabb
load 0
exists 0
exists 1
dump 1 ccdd
exists 1
load 0
load 1
load 2
dumpdir
None-b'\\xaa\\xbb'-True-False-None-True-b'\\xaa\\xbb'-b'\\xcc\\xdd'-'0000:aabb,0001:ccdd'
'''