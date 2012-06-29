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

def _loadkey():
    with open('/etc/histo-key') as f:
        return hex.decode(f.read().strip())

def _myrepo():
    return repo('/var/histo', _loadkey())

class _commithandler(StreamRequestHandler):
    def handle(self):
        with tempfile('histo-server-') as temp:
            ac = _accept(self.rfile, temp)
            _myrepo().commitfile(temp, *ac)

def serveforever():
    server = TCPServer(('0.0.0.0',13750), _commithandler)
    server.serve_forever()