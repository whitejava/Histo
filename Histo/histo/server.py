import os
from stream import objectstream, copy
from socketserver import StreamRequestHandler, TCPServer
from autotemp import tempfile
from ._repo import repo
from threading import Thread
import threading
import time

def _accept(stream, temp):
    #Object stream
    stream = objectstream(stream)
    #Read datetime
    datetime = stream.readobject()
    #Read name
    name = stream.readobject()
    #Read filesize
    filesize = stream.readobject()
    #Read file data into temp
    with open(temp, 'wb') as f:
        copy(stream, f)
    #Check file size.
    assert filesize == os.path.getsize(temp)
    #Return
    return (datetime, name)

def _commithandler(root, key):
    class R:
        def handle(self):
            with tempfile('histo-server-') as temp:
                ac = _accept(self.rfile, temp)
                rp = repo(root, key, _sendfile)
                rp.commitfile(temp, *ac)
                rp.close()
    return R

def _sendfile(path):
    print('send file:', path)

def _acceptservice(root, key):
    server = TCPServer(('0.0.0.0',13750), _commithandler(root, key))
    server.serve_forever()

def _sendservice():
    pass

def serveforever(root, key):
    Thread(lambda:_acceptservice(root, key)).start()
    Thread(lambda:_sendservice()).start()
    while True:
        time.sleep(1)