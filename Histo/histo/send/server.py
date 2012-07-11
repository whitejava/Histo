from diskqueue import diskqueue
from filelock import filelock
from smtp import sendmail
from pclog import log
from netserver import netserver
import hashlib
import pchex
import time
import sys
import os

def main():
    path = sys.argv[1]
    q = diskqueue(path)
    s = service(q)
    s.start()
    while True:
        if not q.empty():
            f = q.front()
            log('sending', f)
            _untilsuccess(lambda:_sendpart(f))
            q.pop()
        time.sleep(1)
    log('shutdown')
    s.shutdown()

class service(netserver):
    def __init__(self, queue):
        netserver.__init__(('0.0.0.0', 13751), self.handle)
        self._queue = queue
    
    def handle(self, stream):
        method = stream.readobject()
        assert method == 'add'
        item = stream.readobject()
        self._queue.append(item)
        stream.writeobject('ok')

def _sendpart(filename):
    name = os.path.basename(filename)
    sender = 'histo@caipeichao.com'
    type = name[0]
    boxid = name[1:]
    boxid = int(boxid)
    boxid = boxid // 5000
    receiver = 'cpc.histo.{}{}@gmail.com'.format(type, boxid)
    log('receiver', receiver)
    with filelock(filename):
        with open(filename, 'rb') as f:
            data = f.read()
    hash = hashlib.new('md5', data).digest()
    hash = pchex.encode(hash)
    sendmail(sender, receiver, name, hash, name, data)

def _untilsuccess(callable):
    while True:
        try:
            return callable()
        except KeyboardInterrupt:
            raise
        except BaseException as e:
            log(str(e))