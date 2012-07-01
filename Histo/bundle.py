import os

class local:
    def __init__(self, root, idformat):
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