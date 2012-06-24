class bundle:
    def __init__(self, root, idformat):
        import os
        os.makedirs(root, exist_ok = True)
        self._root = root
        self._idformat = idformat
    
    def dump(self, id, data):
        with self._open_file(id, 'wb') as f:
            f.write(data)
    
    def load(self, id):
        if not self.exists(id):
            raise KeyError('id not exists')
        with self._open_file(id, 'rb') as f:
            return f.read()
    
    def exists(self, id):
        import os
        return os.path.exists(self._get_file(id))
    
    def _open_file(self, id, mode):
        return open(self._get_file(id), mode)
    
    def _get_file(self, id):
        import os
        return os.path.join(self._root, self._idformat.format(id))