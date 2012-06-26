from unittest import TestCase

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
                result = e
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
        #Print errors
        #Print fails
        for caseid,result in fails:
            print('{:+^20}'.format('Fail'))
            #Print case
            printcase(caseid)
            #Print expect
            print('got: {}'.format(result))
        #Report unittest
        if fails:
            self.fail()
    
    def expecterror(self, method):
        def r(*k):
            try:
                result = method(*k)
            except BaseException as e:
                return e
            else:
                raise Exception('expect error, but {}'.format(result))
        return r