import os
from stream import objectstream, copy
from socketserver import StreamRequestHandler, TCPServer
from autotemp import tempfile, tempdir
from ._repo import repo
from threading import Thread
import threading
import pickle
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

class sendqueue:
    def __init__(self, file):
        self._file = file
        self._lock = threading.Lock()
        if os.path.isfile(file):
            with open(file, 'rb') as f:
                self._queue = pickle.load(f)
        else:
            self._queue = []
            self._save()
    
    def empty(self):
        with self._lock:
            return self._queue == []
    
    def front(self):
        with self._lock:
            return self._queue[0]
    
    def append(self, x):
        with self._lock:
            for i in range(1, len(self._queue)):
                if self._queue[i] == x:
                    del self._queue[i]
                    break
            self._queue.append(x)
            self._save()
    
    def pop(self):
        with self._lock:
            del self._queue[0]
            self._save()
    
    def _save(self):
        with open(self._file, 'wb') as f:
            pickle.dump(self._queue, f)

def _sendfile(path):
    global _sendqueue
    _sendqueue.append(path)

def _acceptservice(root, key):
    class _commithandler(StreamRequestHandler):
        def handle(self):
            #Tempdir for receive request.
            with tempdir('histo-') as td:
                #Stores the file received from network.
                temp = os.path.join(td, 'noname')
                #Resolve request using some protocol
                ac = _accept(self.rfile, temp)
                #Rename the file to be commited.
                temp2 = os.path.join(td, ac[2])
                os.rename(temp, temp2)
                #Log
                log('accept', ac[1])
                #Commit to repo
                rp = repo(root, key, _sendfile)
                rp.commitfile(temp2, time = ac[0], name = ac[1])
                rp.close()
    #Create tcp server
    server = TCPServer(('0.0.0.0',13750), _commithandler)
    #Add shutdown list
    _shutdowns.append(server.shutdown)
    #Log
    log('listening')
    #Run server
    server.serve_forever()

def _sendservice():
    global _sendqueue
    while True:
        if not _sendqueue.empty():
            f = _sendqueue.front()
            log('sending', f)
            time.sleep(5)
            _sendqueue.pop()
        time.sleep(1)

def _startthread(callable):
    Thread(target = callable).start()

def serveforever(root, key):
    global _sendqueue
    _sendqueue = sendqueue(os.path.join(root, 'sendqueue'))
    _startthread(lambda:_acceptservice(root, key))
    _startthread(lambda:_sendservice())
    try:
        while True:
            time.sleep(0.1)
    finally:
        log('shutting down')
        for e in _shutdowns: e()