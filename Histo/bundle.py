import os

class local:
    def __init__(self, root, idformat):
        if not os.path.exists(root): os.makedirs(root)
        self._root = root
        self._idformat = idformat
    
    def dump(self, id, data):
        id = self._idformat.format(id)
        path = os.path.join(self._root, id)
        with open(path, 'wb') as f:
            f.write(data)
    
    def load(self, id):
        id = self._idformat.format(id)
        path = os.path.join(self._root, id)
        with open(path, 'rb') as f:
            return f.read()
    
    def exists(self, id):
        id = self._idformat.format(id)
        path = os.path.join(self._root, id)
        return os.path.isfile(path)

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
        return self._buundle.exists(id)

class monitor:
    def __init__(self, bundle):
        self._bundle = bundle
    
    def dump(self, id, data):
        self._bundle.dump(id, data)
        self._changes.add(id)
    
    def load(self, id):
        return self._bundle.load(id)
    
    def exists(self, id):
        return self._bundle.exists(id)
    
    def changes(self):
        return self._changes[:]