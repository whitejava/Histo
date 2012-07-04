import os
from stream import objectstream, copy
from socketserver import StreamRequestHandler, TCPServer
from autotemp import tempfile, tempdir
from ._repo import repo
from threading import Thread
import time

_shutdowns = []

def _accept(stream, temp):
    #Object stream
    stream = objectstream(stream)
    #Read datetime
    datetime = stream.readobject()
    #Read name
    name = stream.readobject()
    #Read filename
    filename = stream.readobject()
    #Read filesize
    filesize = stream.readobject()
    #Read file data into temp
    with open(temp, 'wb') as f:
        copy(stream, f)
    #Check file size.
    assert filesize == os.path.getsize(temp)
    #Return
    return (datetime, name, filename)

def log(*message):
    t = '[{:13f}]'.format(time.clock())
    print(t, *message)

def _sendfile(path):
    log('send file:', path)

def _acceptservice(root, key):
    class _commithandler(StreamRequestHandler):
        def handle(self):
            with tempdir('histo-server-') as td:
                temp = os.path.join(td, 'noname')
                ac = _accept(self.rfile, temp)
                temp2 = os.path.join(td, ac[2])
                os.rename(temp, temp2)
                log('accept', ac[1])
                rp = repo
                rp = repo(root, key, _sendfile)
                rp.commitfile(temp2, time = ac[0], name = ac[1])
                rp.close()
    server = TCPServer(('0.0.0.0',13750), _commithandler)
    _shutdowns.append(server.shutdown)
    log('listening')
    server.serve_forever()

def _sendservice():
    pass

def _startthread(callable):
    Thread(target = callable).start()

def serveforever(root, key):
    _startthread(lambda:_acceptservice(root, key))
    _startthread(lambda:_sendservice())
    try:
        while True:
            time.sleep(0.1)
    finally:
        log('shutting down')
        for e in _shutdowns: e()