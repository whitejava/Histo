import unittest
from .cipher import cipher
from timer import timer

#2012 06 09 0.20145043181969796 win7/Core i5
#2012 06 11 0.20845242799156374 win7/Core i5
#2012 06 11 0.19000000000000003 ubuntu1204/vmware/win7/Core i5
#2012 06 26 0.32000000000000030 ubuntu1204/vmware/win7/70% Core i5
#2012 06 26 0.16999999999999993 ubuntu1204/vmware/win7/Core i5
#2012 06 26 0.15000000000000013 ubuntu1204/vmware/win7/Core i5
class test(unittest.TestCase):
    def test_encrypt(self):
        #Cipher
        c = cipher(bytes(32))
        #Several times
        for _ in range(10):
            #Timer
            with timer():
                #Encrypt regular data.
                c.encode(b'1'*(10*1024*1024+1))