from diskqueue import diskqueue
from filelock import filelock
from smtp import sendmail
from pclog import log
import hashlib
import pchex
import time
import os

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

class service:
    def __init__(self, root):
        path = os.path.join(root, 'sendqueue')
        self._queue = diskqueue(path)
    
    def run(self):
        while True:
            if not self._queue.empty():
                f = self._queue.front()
                log('sending', f)
                _untilsuccess(lambda:_sendpart(f))
                self._queue.pop()
            time.sleep(0.1)
        log('send shutdown')
    
    def addqueue(self, filename):
        self._queue.append(filename)