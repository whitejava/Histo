from pctest import testcase,dumpdir,runins,createfiles
from autotemp import tempdir
from bundle import local
import dfile
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(partsize, *k):
    class a: pass
    self = a()
    partsize = eval(partsize)
    with tempdir('dfile-write-') as temp:
        def open():
            bundle = local(temp, '{}')
            self.file = dfile.open(bundle, partsize, 'wb')
        t = {'open': open,
             'write': lambda x:self.file.write(hex.decode(x)),
             'close': lambda:self.file.close(),
             'createfiles': lambda x:createfiles(temp,x),
             'dumpdir': lambda:dumpdir(temp),
             'changes': lambda:list(self.file.changes())}
        return runins(t, k)

data = \
'''
3
open
changes
dumpdir
write 00112233
changes
dumpdir
changes
write 44556677
changes
dumpdir
close
changes
dumpdir
[]--[1]-1:001122-[1]-[1, 2]-1:001122,2:334455-[0, 1, 2, 3]-0:80034b032e80034b082e80034302667771002e,1:001122,2:334455,3:6677

3
createfiles 0:80034b032e80034b082e80034302667771002e
open
changes
write 88990011
changes
dumpdir
changes
close
changes
dumpdir
[]-[3, 4]-0:80034b032e80034b082e80034302667771002e,3:667788,4:990011-[3, 4]-[0, 3, 4]-0:80034b032e80034b0c2e8003430071002e,3:667788,4:990011

3
createfiles 0:80034b032e80034b082e800343016671002e
open
changes
write 778899
changes
dumpdir
changes
close
changes
dumpdir
AssertionError()-AttributeError("\'a\' object has no attribute \'file\'",)-AttributeError("\'a\' object has no attribute \'file\'",)-AttributeError("\'a\' object has no attribute \'file\'",)-0:80034b032e80034b082e800343016671002e-AttributeError("\'a\' object has no attribute \'file\'",)-AttributeError("\'a\' object has no attribute \'file\'",)-AttributeError("\'a\' object has no attribute \'file\'",)-0:80034b032e80034b082e800343016671002e

0
open
write 1122
dumpdir
close
dumpdir
AssertionError()-AttributeError("\'a\' object has no attribute \'file\'",)--AttributeError("\'a\' object has no attribute \'file\'",)-

2
createfiles 0:80034b032e80034b082e80034302667771002e
open
write 112233
dumpdir
close
dumpdir
AssertionError()-AttributeError("\'a\' object has no attribute \'file\'",)-0:80034b032e80034b082e80034302667771002e-AttributeError("\'a\' object has no attribute \'file\'",)-0:80034b032e80034b082e80034302667771002e

3
open
dumpdir
close
dumpdir
write 11
dumpdir
-0:80034b032e80034b002e8003430071002e-AssertionError()-0:80034b032e80034b002e8003430071002e
'''