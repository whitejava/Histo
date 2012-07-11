from socketserver import TCPServer, StreamRequestHandler
from .._repo import _securedfile
from bundle import local, crypto
from cipher import aes
from pclog import log
from stream import iostream, objectstream, copy
import pickle
import dfile
import io
import os

index = []
reporoot = None

def serveforever(root, key):
    reporoot = root
    f = _securedfile(os.path.join(root, 'index'), key, 'i{:06d}', 1024*1024)
    data = f.read()
    datalen = len(data)
    f.close()
    data = io.BytesIO(data)
    while data.tell() < datalen:
        item = pickle.load(data)
        index.append(dict(item))
    class _requesthandler(StreamRequestHandler):
        def handle(self):
            stream = iostream(self.rfile, self.wfile)
            stream = objectstream(stream)
            type = stream.readobject()
            t = {'search': _search,
                 'get': _get}
            t[type](stream)
                
    server = TCPServer(('0.0.0.0',13777), _requesthandler)
    log('listening')
    server.serve_forever()

def _search(stream):
    keyword = stream.readobject()
    result = []
    for e in index:
        for e2 in _walksummary(index['summary']):
            if e2.find(keyword) >= 0:
                result.append(e)
                break
    stream.writeobject(result)

def _get(stream):
    range = stream.readobject()
    f = _securedfile(os.path.join(reporoot, 'data'))
    f.seek(range[0])
    copy(f, stream, range[1] - range[0])
    f.close()

def _securedfile(self, root, key, idformat, partsize):
    b = []
    #Local bundle
    b.append(local(root, idformat))
    #Verify
    b.append(crypto(b[-1], hash.cipher('md5')))
    b.append(crypto(b[-1], hash.cipher('sha1')))
    #Encrypt
    b.append(crypto(b[-1], aes.cipher(key)))
    #Verify
    b.append(crypto(b[-1], hash.cipher('md5')))
    b.append(crypto(b[-1], hash.cipher('sha1')))
    #DFile
    return dfile.open(b[-1], partsize, 'rb')

def _walksummary(summary):
    if type(summary) is tuple:
        if summary and type(summary[0]) is str:
            yield summary[0]
            for e in _walksummary(summary[1]):
                yield e
        else:
            for e in summary:
                for f in _walksummary(e):
                    yield f
    elif type(summary) is str:
        yield summary