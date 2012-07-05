from . import _accept as accept
from threading import Thread
from . import _send as send
from pclog import log
import time

def serveforever(root, key):
    sendservice = send.service(root)
    acceptservice = accept.service(root, key, sendservice)
    Thread(target = acceptservice.run).start()
    Thread(target = sendservice.run).start()
    try:
        while True:
            time.sleep(0.1)
    finally:
        log('shutting down')
        acceptservice.shutdown()