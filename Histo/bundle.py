import os, smtp, time, io
from pclib import filelock

class local:
    def __init__(self, root, idformat):
        if not os.path.exists(root): os.makedirs(root)
        self._root = root
        self._idformat = idformat
    
    def dump(self, n, data):
        path = self.getpath(n)
        with filelock(path):
            with open(path, 'wb') as f:
                f.write(data)
    
    def load(self, n):
        path = self.getpath(n)
        with filelock(path):
            with open(path, 'rb') as f:
                return f.read()
    
    def exists(self, n):
        path = self.getpath(n)
        return os.path.isfile(path)
    
    def getpath(self, n):
        n = self._idformat.format(n)
        path = os.path.join(self._root, n)
        return path

class local2:
    def __init__(self, root):
        if not os.path.exists(root):
            os.makedirs(root)
        self.root = root
    
    def open(self, name, mode):
        return open(os.path.join(self.root, name), mode)
    
    def list(self):
        return os.listdir(self.root)

class limit:
    def __init__(self, bundle, writespeed, readspeed):
        self.bundle = bundle
        self.writespeed = writespeed
        self.readspeed = readspeed
    
    def open(self, name, mode):
        f = self.bundle.open(name, mode)
        if mode == 'rb':
            return limitreader(f, self.readspeed)
        elif mode == 'wb':
            return limitwriter(f, self.writespeed)
        else:
            raise Exception('Mode error.')

def speedlimit(speed, bytes):
    maxsleep = 0.1
    while bytes:
        sleep = bytes / speed
        if sleep > maxsleep:
            sleep = maxsleep
        readbytes = sleep * speed
        if readbytes > bytes:
            readbytes = bytes
        time.sleep(sleep)
        yield readbytes
        bytes -= readbytes

class limitreader:
    def __init__(self, file, speed):
        self.file = file
        self.speed = speed
        
    def read(self, limit):
        result = bytearray()        
        for e in speedlimit(self.speed, limit):
            read = self.file.read(limit)
            if not read:
                break
            result.extend(read)
        return result

class limitwriter:
    def __init__(self, file, speed):
        self.file = file
        self.speed = speed
    
    def write(self, data):
        io = io.BytesIO(data)
        for e in speedlimit(self.speed, len(data)):
            x = io.read(e)
            assert len(x) is e
            self.file.write(x)

class crypto:
    def __init__(self, bundle, cipher):
        self._bundle = bundle
        self._cipher = cipher
    
    def dump(self, n, data):
        data = self._cipher.encode(data)
        self._bundle.dump(n, data)
    
    def load(self, n):
        data = self._bundle.load(n)
        data = self._cipher.decode(data)
        return data
    
    def exists(self, n):
        return self._bundle.exists(n)

class listen:
    def __init__(self, bundle, listener):
        self._bundle = bundle
        self._listener = listener
    
    def dump(self, n, data):
        self._bundle.dump(n, data)
        self._listener(n)
    
    def load(self, n):
        return self._bundle.load(n)
    
    def exists(self, n):
        return self._bundle.exists(n)

class mail:
    def __init__(self, sender, mail, password):
        self._sender = sender
        self._mail = mail
        self._password = password
    
    def dump(self, n, data, stopper = [False]):
        sender = self._sender
        receiver = self._mail
        subject = str(n)
        content = ''
        attachmentname = str(n)
        attachmentdata = data
        smtp.sendmail(sender, receiver, subject, content, attachmentname, attachmentdata, stopper)
    
    def load(self, n):
        raise Exception('not impl')
    
    def delete(self, n):
        raise Exception('not impl')