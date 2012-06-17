import unittest

def get_test_filename(filename):
    import os
    no_extension = __file__[:-3]
    return os.path.join(no_extension, filename) 

class test(unittest.TestCase):
    def setUp(self):
        test_names = 'GFSbox','KeySbox','VarKey','VarTxt'
        relative_filenames = ['CBC{}256.rsp'.format(e) for e in test_names]
        self._filenames = [get_test_filename(e) for e in relative_filenames]
    
    def test_vector(self):
        for filename in self._filenames:
            suite = self._load_suite(filename)
            self._run_suite(suite)
    
    def _run_suite(self, suite):
        for case in suite:
            self._run_case(case)
    
    def _run_case(self, case):
        from .cipher import cipher
        key = case['key']
        iv = case['iv']
        input = case['input']
        output = case['output']
        method = case['method']
        cipher = cipher(key)
        if method == 'encrypt':
            call = cipher._encrypt_with_iv_no_padding
        else:
            call = cipher._decrypt_with_iv_no_padding
        actual = call(input, iv)
        from hex import hex
        print('{} {} key {} iv {} = {}'.format(method, hex.encode(input), hex.encode(key), hex.encode(iv), hex.encode(output)))
        self.assertEquals(output, actual)

    def _load_suite(self,filename):
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
        from hex import hex
        for m,e in zip(['encrypt','decrypt'],a):
            for i in range(0,len(e),5):
                d = {}
                for j in range(5):
                    s = e[i+j].split('=')
                    left = s[0].strip()
                    right = s[1].strip()
                    if left != 'COUNT':
                        right = hex.decode(right)
                    d[left] = right
                y = {'method':m,
                     'key':d['KEY'],
                     'iv':d['IV']}
                if m == 'encrypt':
                    y['input'] = d['PLAINTEXT']
                    y['output'] = d['CIPHERTEXT']
                else:
                    y['input'] = d['CIPHERTEXT']
                    y['output'] = d['PLAINTEXT']
                yield y