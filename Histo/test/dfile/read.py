from pctest import testcase,createfiles,runins,dumpdir
from autotemp import tempdir
from bundle import local
import dfile
import hex

class test(testcase):
    def test(self):
        self.bulktest(data, func)

def func(partsize, creates, *k):
    partsize = eval(partsize)
    with tempdir('dfile-read-') as temp:
        createfiles(temp, creates)
        bundle = local(temp, '{}')
        file = dfile.open(bundle, partsize, 'rb')
        t = {'read': lambda x:hex.encode(file.read(eval(x))),
             'seek': lambda x:file.seek(eval(x)),
             'close': lambda: file.close(),
             'available': lambda: file.available()}
        return runins(t,k)

data = \
'''
3
0:80034b032e80034b082e80034302667771002e,1:001122,2:334455,3:6677
available
read 2
available
read None
available
seek 4
available
read 3
available
read 3
available
read 3
available
8-0011-6-223344556677-0-4-445566-1-77-0--0

3
0:80034b032e80034b082e80034302667771002e,1:001122,2:334455,3:6677
seek -1
read 4
seek 8
read 3
seek 9
read 3
seek 0
read -1
read 0
AssertionError()-00112233--AssertionError()--AssertionError()-

3
0:80034b032e80034b082e80034302667771002e,2:334455,3:6677
read 4
seek 3
read 3
IOError(2, 'No such file or directory')-334455

2
0:80034b032e80034b082e80034302667771002e,2:334455,3:6677
read 1
read 1
AssertionError()

3
0:80034b032e80034b082e80034302667771002e,1:0011,2:334455aabb,3:6677
read 2
read 1
seek 3
read 4
0011-AssertionError()-33445566
'''