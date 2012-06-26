import unittest
from .cipher import cipher
from timer import timer

#2012 06 09 0.20145043181969796 win7
#2012 06 11 0.20845242799156374 win7
#2012 06 11 0.19000000000000003 ubuntu1204/vmware
#2012 06 26 0.32000000000000030 ubuntu1204/vmware
#2012 06 26 0.16999999999999993 ubuntu1204/vmware
class test(unittest.TestCase):
    def test_encrypt(self):
        #Key
        key = bytes(32)
        #Cipher
        c = cipher(key)
        #Several times
        for _ in range(10):
            #Timer
            with timer():
                #Data size
                datasize = 10*1024*1024
                #Data
                data = b'1'*datasize+b'2'
                #Encrypt
                c.encrypt(data)