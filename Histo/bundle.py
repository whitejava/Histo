import os
from filelock import filelock

class local:
    def __init__(self, root, idformat):
        if not os.path.exists(root): os.makedirs(root)
        self._root = root
        self._idformat = idformat
    
    def dump(self, id, data):
        path = self.getpath(id)
        with filelock(path):
            with open(path, 'wb') as f:
                f.write(data)
    
    def load(self, id):
        path = self.getpath(id)
        with filelock(path):
            with open(path, 'rb') as f:
                return f.read()
    
    def exists(self, id):
        path = self.getpath(id)
        return os.path.isfile(path)
    
    def getpath(self, id):
        id = self._idformat.format(id)
        path = os.path.join(self._root, id)
        return path

class crypto:
    def __init__(self, bundle, cipher):
        self._bundle = bundle
        self._cipher = cipher
    
    def dump(self, id, data):
        data = self._cipher.encode(data)
        self._bundle.dump(id, data)
    
    def load(self, id):
        data = self._bundle.load(id)
        data = self._cipher.decode(data)
        return data
    
    def exists(self, id):
        return self._bundle.exists(id)

class monitor:
    def __init__(self, bundle, listener):
        self._bundle = bundle
        self._listener = listener
    
    def dump(self, id, data):
        self._bundle.dump(id, data)
        self._listener(id)
    
    def load(self, id):
        return self._bundle.load(id)
    
    def exists(self, id):
        return self._bundle.exists(id)