#- - encoding: utf8

from subprocess import Popen, STDOUT, PIPE
from datetime import datetime
import time, struct, pickle, hashlib
import socket
from socketserver import TCPServer, StreamRequestHandler
from threading import Thread
import threading, os, stat, shutil
import tempfile as otemp

def quietcall(commands):
    proc = Popen(commands, stdin = None, stderr = STDOUT, stdout = PIPE)
    while True:
        try:
            proc.communicate()
        except ValueError as e:
            if e.args[0] == 'I/O operation on closed file':
                break
            else:
                raise
    return proc.wait()

class byteshex:
    @staticmethod
    def encode(x):
        return ''.join(['{:02x}'.format(e) for e in x])
    
    @staticmethod
    def decode(x):
        assert len(x) % 2 == 0
        return bytes([int(x[i:i+2],16) for i in range(0,len(x),2)])

def timetuple(t):
    return (t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond)

def nowtuple():
    return timetuple(datetime.now())

class timer:
    def __init__(self, handle = print):
        self.handle = handle
    
    def __enter__(self):
        self._time = time.clock()
    
    def __exit__(self,*k):
        self.handle(time.clock() - self._time)

def copystream2(input, output):
    for e in chunkreader(input, limit=None, chunksize=128*1024):
        output.write(e)

def copystream(input, output, limit = None, chunksize = 128*1024, buffercount = 4):
    from queue import Queue
    b = Queue(buffercount)
    class readthread(Thread):
        def __init__(self, buffer):
            Thread.__init__(self)
            self.buffer = buffer
        def run(self):
            b = self.buffer
            for e in chunkreader(input, limit=limit, chunksize=chunksize):
                b.put(e)
            b.put(None)
    rthread = readthread(b)
    rthread.start()
    result = 0
    while True:
        e = b.get()
        if e is None:
            break
        output.write(e)
        result += len(e)
    return result
    
def chunkreader(input, limit, chunksize):
    if limit is None:
        while True:
            read = input.read(chunksize)
            if not read:
                break
            yield read
    else:
        while limit > 0:
            readsize = min(chunksize, limit)
            read = input.read(readsize)
            if not read:
                break
            yield read
            limit -= len(read)

def bufferedreader(reader, buffercount = 5):
    buffer = []
    reading = True
    threadrunning = True
    def readthread():
        for e in reader:
            if len(buffer) < buffercount:
                buffer.append(e)
            else:
                while threadrunning and len(buffer) >= buffercount:
                    time.sleep(0.1)
        reading = False
    while reading:
        if buffer:
            yield buffer[0]
            del buffer[0]
        else:
            while reading and not buffer:
                time.sleep(0.1)

class datastream:
    def __init__(self, stream):
        self._stream = stream
    
    def write(self, data):
        self._stream.write(data)
    
    def writeint(self, a):
        self.write(struct.pack('!i', a))
    
    def writelong(self, a):
        self.write(struct.pack('!q',a))
    
    def writebytes(self, a):
        self.writeint(len(a))
        self.write(a)
    
    def read(self, limit = None):
        return self._stream.read(limit)
    
    def readfully(self, limit):
        result = bytearray()
        while limit > 0:
            read = self.read(limit)
            if not read:
                raise EOFError()
            result.extend(read)
            limit -= len(read)
        return bytes(result)
    
    def readint(self):
        return struct.unpack('!i', self.readfully(4))[0]
    
    def readlong(self):
        return struct.unpack('!q', self.readfully(8))[0]
    
    def readbytes(self):
        length = self.readint()
        result = self._stream.read(length)
        assert len(result) == length
        return result
    
class objectstream:
    def __init__(self, stream):
        self._stream = datastream(stream)
        
    def write(self, data):
        self._stream.write(data)
    
    def read(self, limit = None):
        return self._stream.read(limit)
    
    def writeobject(self, object):
        dump = pickle.dumps(object)
        self._stream.writeint(len(dump))
        self._stream.write(dump)
    
    def readobject(self):
        length = self._stream.readint()
        dump = self._stream.readfully(length)
        assert len(dump) == length
        return pickle.loads(dump)

class tcpstream:
    def __init__(self, target):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect(target)
    
    def write(self, data):
        self._sock.sendall(data)
    
    def read(self, limit = None):
        if limit == None:
            limit = 1024
        return self._sock.recv(limit)

    def close(self):
        self._sock.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()
        
class iostream:
    def __init__(self, input, output):
        self._input = input
        self._output = output
    
    def write(self, data):
        self._output.write(data)
    
    def read(self, limit = None):
        return self._input.read(limit)

class hashstream:
    def __init__(self, algorithm):
        self._hasher = hashlib.new(algorithm)
    
    def write(self, data):
        self._hasher.update(data)
    
    def digest(self):
        return self._hasher.digest()

class streamhub:
    def __init__(self, *streams):
        self.streams = streams
    
    def write(self, data):
        threads = []
        for e in self.streams:
            threads.append(Thread(target=lambda:e.write(data)))
        for e in threads:
            e.start()
        for e in threads:
            e.join()

class netserver:
    def __init__(self, address, handler):
        class a(StreamRequestHandler):
            def handle(self):
                stream = iostream(self.rfile, self.wfile)
                stream = objectstream(stream)
                handler(stream)
        self._server = TCPServer(address, a)
    
    def start(self):
        Thread(target = self.run).start()
    
    def run(self):
        self._server.serve_forever()
    
    def shutdown(self):
        self._server.shutdown()

class filelockhost:
    def __init__(self):
        self._locks = dict()
        self._lock = threading.Lock()
    
    def acquire(self, path):
        with self._lock:
            if path not in self._locks:
                self._locks[path] = threading.Lock()
            self._locks[path].acquire()
    
    def release(self, path):
        with self._lock:
            self._locks[path].release()
            del self._locks[path]
            
filelockhostinstance = filelockhost()

class filelock:
    def __init__(self, path):
        self._path = path
    
    def acquire(self):
        filelockhostinstance.acquire(self._path)
    
    def release(self):
        filelockhostinstance.release(self._path)
    
    def __enter__(self):
        self.acquire()
    
    def __exit__(self,t,v,trace):
        self.release()

class tempfile:
    def __init__(self, prefix = 'tmp', suffix = '', dir = None):
        self._prefix = prefix
        self._suffix = suffix
        self._dir = dir
    
    def __enter__(self):
        self._temp = otemp.NamedTemporaryFile('wb', suffix = self._suffix, prefix=self._prefix, dir=self._dir, delete=False)
        self._temp.close()
        return self._temp.name
    
    def __exit__(self, *k):
        os.remove(self._temp.name)

def _forceremove(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)

class tempdir:
    def __init__(self, prefix = 'tmp', suffix = '', dir = None):
        self._prefix = prefix
        self._suffix = suffix
        self._dir = dir
    
    def __enter__(self):
        self._temp = otemp.mkdtemp(self._suffix, self._prefix, self._dir)
        return self._temp
    
    def __exit__(self, *k):
        shutil.rmtree(self._temp, onerror = _forceremove)

def wait_for_keyboard_interrupt():
    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        return

def ceildiv(a,b):
    if a%b is 0:
        return a//b
    else:
        return a//b+1

def unzip(d,k):
    d = dict(d)
    r = []
    for e in k:
        r.append(d[e])
        del d[e]
    assert not d
    return r

def loadconfig(configfile):
    result = dict()
    with open(configfile ,'rb', encode='utf8') as f:
        for e in f:
            e = e.strip()
            if e.startswith('#'):
                continue
            e = e.split('=', limit=1)
            e = [e2.strip() for e2 in e]
            e[1] = eval(e[1])
            result[e[0]] = e[1]
    return result

def hook(func, target):
    def a(*k, **kw):
        return target(func, *k, **kw)
    return a

def timetext(time = None, format = '%04d%02d%02d%02d%02d%02d%06d'):
    return format % nowtuple()

def limitrange(x, min, max):
    if x < min: x = min
    if x > max: x = max
    return x

def ignoreexception(callable):
    try:
        callable()
    except Exception:
        pass