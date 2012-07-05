from . import _accept as accept
from threading import Thread
from . import _send as send
from pclog import log

def serveforever(root, key):
    try:
        sendservice = send.service(root)
        acceptservice = accept.service(root, key, sendservice)
        Thread(target = acceptservice.run).start()
        sendservice.run()
    except KeyboardInterrupt:
        log('shutting down')
        acceptservice.shutdown()