from subprocess import Popen, STDOUT, PIPE
from datetime import datetime

def quietcall(commands):
    proc = Popen(commands, stdin = None, stderr = STDOUT, stdout = PIPE)
    while True:
        try:
            proc.communicate()
        except ValueError as e:
            if e.args[0] == 'I/O operation on closed file':
                break
            else:
                raise
    return proc.wait()

class byteshex:
    @staticmethod
    def encode(x):
        return ''.join(['{:02x}'.format(e) for e in x])
    
    @staticmethod
    def decode(x):
        assert len(x) % 2 == 0
        return bytes([int(x[i:i+2],16) for i in range(0,len(x),2)])

def timetuple(t):
    return (t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond)

def nowtuple():
    return timetuple(datetime.now())