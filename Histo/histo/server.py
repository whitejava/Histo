import os
from stream import objectstream, copy
from socketserver import StreamRequestHandler, TCPServer
from autotemp import tempfile
from ._repo import repo

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
                rp = repo(root, key)
                rp.commitfile(temp, *ac)
                rp.close()
    return R

def serveforever(root, key):
    server = TCPServer(('0.0.0.0',13750), _commithandler(root, key))
    server.serve_forever()