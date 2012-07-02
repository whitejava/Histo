from pctest import testcase,dumpdir,runins,createfiles
from autotemp import tempdir
from bundle import local
import dfile
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, self.func)
        
    def func(self, partsize, *k):
        partsize = eval(partsize)
        with tempdir('dfile-write-') as temp:
            def open():
                bundle = local(temp, '{}')
                self.file = dfile.open(bundle, partsize, 'wb')
            t = {'open': open,
                 'write': lambda x:self.file.write(hex.decode(x)),
                 'close': lambda:self.file.close(),
                 'createfiles': lambda x:createfiles(temp,x),
                 'dumpdir': lambda:dumpdir(temp)}
            return runins(t, k)

data = \
'''
3
open
dumpdir
write 00112233
dumpdir
write 44556677
dumpdir
close
dumpdir
-1:001122-1:001122,2:334455-0:80034b032e80034b082e80034302667771002e,1:001122,2:334455,3:6677

3
createfiles 0:80034b032e80034b082e80034302667771002e
open
write 88990011
dumpdir
close
dumpdir
0:80034b032e80034b082e80034302667771002e,3:667788,4:990011-0:80034b032e80034b0c2e8003430071002e,3:667788,4:990011

3
createfiles 0:80034b032e80034b082e800343016671002e
open
write 778899
dumpdir
close
dumpdir
AssertionError()-AssertionError()-0:80034b032e80034b082e800343016671002e-AssertionError()-0:80034b032e80034b082e800343016671002e

0
open
write 1122
dumpdir
close
dumpdir
AssertionError()-AssertionError()--AssertionError()-

2
createfiles 0:80034b032e80034b082e80034302667771002e
open
write 112233
dumpdir
close
dumpdir
AssertionError()-AssertionError()-0:80034b032e80034b082e80034302667771002e-AssertionError()-0:80034b032e80034b082e80034302667771002e

3
open
dumpdir
close
dumpdir
write 11
dumpdir
-0:80034b032e80034b002e8003430071002e-AssertionError()-0:80034b032e80034b002e8003430071002e
'''