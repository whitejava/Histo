from socketserver import TCPServer, StreamRequestHandler
from stream import objectstream, copy, iostream
from autotemp import tempdir
from ._repo import repo
from pclog import log
import os

def _accept(root, key, sendservice, stream):
    stream = objectstream(stream)
    with tempdir('histo-') as td:
        #Read paramters
        time = stream.readobject()
        name = stream.readobject()
        log('accept', name)
        filename = stream.readobject()
        filesize = stream.readobject()
        #Read file data into temp file
        log('retrieving file data')
        temp = os.path.join(td, filename)
        with open(temp, 'wb') as f:
            copy(stream, f, limit = filesize)
        #Ensure read size
        assert filesize == os.path.getsize(temp)
        #Commit to repo
        log('committing to repo')
        rp = repo(root, key, sendservice.addqueue)
        rp.commitfile(temp, time = time, name = name)
        rp.close()
        #Response OK
        stream.writeobject('OK')
        log('done')

class service:
    def __init__(self, root, key, sendservice):
        class _commithandler(StreamRequestHandler):
            def handle(self):
                stream = iostream(self.rfile, self.wfile)
                _accept(root, key, sendservice, stream)
        self._server = TCPServer(('0.0.0.0',13750), _commithandler)
        log('listening')
    
    def run(self):
        log('running')
        self._server.serve_forever()

    def shutdown(self):
        self._server.shutdown()