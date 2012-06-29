from pctest import testcase
import hex
import io
from stream import objectstream

class test(testcase):
    def test_write(self):
        self.batchtest(wdata, 1, write, (eval, hex.encode))
    def test_writeread(self):
        self.batchtest(rwdata, 1, readwrite, (eval, repr))

def write(x):
    #Create buffer
    buffer = io.BytesIO()
    #Write object
    objectstream(buffer).writeobject(x)
    #Return bytes
    return buffer.getvalue()

def readwrite(x):
    return objectstream(io.BytesIO(write(x))).readobject()

wdata = \
'''
None
80034e2e

123
80034b7b2e

1.1
8003473ff199999999999a2e

1.1111111111111112
8003473ff1c71c71c71c722e

1111111111111111111111111111111111111111111111
80038a13c7711cc7715c5f0c4074f66db506eb15eed2312e

b'bytes'
80034305627974657371002e

'string'
80035806000000737472696e6771002e

(1, 2, 3)
80034b014b024b038771002e

[1, 2, 3]
80035d7100284b014b024b03652e

bytearray(b'bytearray')
8003636275696c74696e730a6279746561727261790a71005809000000627974656172726179710158070000006c6174696e2d3171028671035271042e

'\ucccc'
80035803000000ecb38c71002e

['complex', (1, b'123', 2, 3, 12.1, ['abc'])]
80035d7100285807000000636f6d706c65787101284b01430331323371024b024b034740283333333333335d71035803000000616263710461747105652e
'''

split = wdata.splitlines()
rwdata = '\n'+'\n\n'.join(['\n'.join([split[i], split[i]]) for i in range(1,len(split),3)])