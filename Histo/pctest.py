from unittest import TestCase
from listfiles import listfiles
import traceback
import hex
import os

def dumpdir(folder):
    #List files
    files = listfiles(folder)
    #Define result
    result = []
    #For each file.
    #Use sorted to get the same result.
    for file in sorted(files):
        #Full path
        path = os.path.join(folder, file)
        #Read content
        with open(path,'rb') as f:
            #Read
            content = f.read()
            #To hex
            content = hex.encode(content)
            #Format as "file:data"
            item = ':'.join([file, content])
            #Output
            result.append(item)
    #Format as "item,item,item"
    return ','.join(result)

def gettestfile(filename, source = None):
    callerfile = traceback.extract_stack()[-2][0]
    if source:
        return os.path.join(os.path.dirname(callerfile), source, filename)
    else:
        return os.path.join(callerfile[:-3], filename)

def _split(a,sep):
    result = [[]]
    for e in a:
        if e == sep:
            result.append([])
        else:
            result[-1].append(e)
    return result

class testcase(TestCase):
    def setUp(self):
        self._pc_cleanups = []
    
    def tearDown(self):
        for e in self._pc_cleanups:
            e()

    def batchtest(self, data, paramcount, method, format):
        #Split data by line.
        data = data.split('\n')
        #Strip first line, because it's empty.
        data = data[1:]
        #Group lines according to paramcount.
        data = [[data[i+j] for j in range(paramcount+1)]for i in range(0,len(data),paramcount+2)]
        #Get params from data.
        params0 = [[e[i] for i in range(paramcount)] for e in data]
        #Format params.
        params = [[format[i](e[i])for i in range(len(e))]for e in params0]
        #Get expects from data.
        expects = [e[paramcount] for e in data]
        #Define fails
        fails = []
        #Run cases.
        for i in range(len(params)):
            #Call method
            try:
                result = method(*params[i])
            except BaseException as e:
                result = repr(e)
                traceback.print_exception(type(e), e, False)
            else:
                #Format result
                result = format[paramcount](result)
            #Check result.
            if result != expects[i]:
                fails.append((i, result))
        def printcase(n):
            #Print case number
            print('Case {}'.format(n))
            #Print params
            for e in params0[n]:
                print(e)
            #Print expect
            print('expect: {}'.format(expects[n]))
        #Print fails
        for caseid,result in fails:
            print('{:+^20}'.format('Fail'))
            #Print case
            printcase(caseid)
            #Print expect
            print('got:\n{}'.format(result))
        #Report unittest
        if fails:
            self.fail()
    
    def bulktest(self, data, func):
        #Assume no fails.
        fail = False
        #Split data
        lines = data.splitlines()
        #Iterator every case
        for e in _split(lines, '')[1:]:
            try:
                result = func(*e[:-1])
                expect = e[-1]
                errormessage = ''
            except BaseException as ex:
                result = repr(ex)
                expect = e[-1]
                errormessage = ''.join(traceback.format_exception(type(ex), ex, False))
            if result != expect:
                fail = True
                print('{:+^20}'.format('Fail'))
                print(*e,sep='\n')
                print(result)
                print(errormessage)
        self.assertFalse(fail)