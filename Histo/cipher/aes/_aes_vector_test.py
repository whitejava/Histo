import unittest
from .cipher import cipher

def tobytes(a):
    return bytes([int(a[i:i+2],16)for i in range(0,len(a),2)])

def tohex(b):
    return ''.join(['{:02x}'.format(e) for e in b])

class test(unittest.TestCase):
    def test_vector_test(self):
        v = ['CBC{}256.rsp'.format(e) for e in ('GFSbox','KeySbox','VarKey','VarTxt')]
        for e in v:
            self._test_vector(e)
    
    def _test_vector(self,v):
        import os
        filename = os.path.join(os.path.dirname(__file__),'_vector_data',v)
        for e in self._read_cases(filename):
            self._run_test_case(e)
        
    def _run_test_case(self,case):
        key = tobytes(case['KEY'])
        c = cipher(key)
        text = tobytes(case['PLAINTEXT'])
        iv = tobytes(case['IV'])
        code = tobytes(case['CIPHERTEXT'])
        if case['method'] == 'encrypt':
            actual = c._encrypt_with_iv_no_padding(text,iv)
            print('encrypt {} key {} iv {} gets {}'.format(tohex(text),tohex(key),tohex(iv),tohex(actual))) 
            self.assertEqual(actual, code)
        elif case['method'] == 'decrypt':
            actual = c._decrypt_with_iv_no_padding(code,iv)
            print('decrypt {} key {} iv {} gets {}'.format(tohex(code),tohex(key),tohex(iv),tohex(actual)))
            self.assertEqual(actual, text)
        else:
            self.fail('unknown method')
        
    def _read_cases(self,filename):
        a = [[],[]]
        with open(filename,'r') as f:
            f = iter([e[:-1] for e in f])
            for e in f:
                if e == '[ENCRYPT]':
                    break
            for e in f:
                if e == '[DECRYPT]':
                    break
                elif e:
                    a[0].append(e)
            for e in f:
                if e:
                    a[1].append(e)
        for m,e in zip(['encrypt','decrypt'],a):
            for i in range(0,len(e),5):
                d = {'method':m}
                for j in range(5):
                    s = e[i+j].split('=')
                    d[s[0].strip()]=s[1].strip()
                yield d