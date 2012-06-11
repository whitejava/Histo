class bundle:
    def __init__(self):
        self.files = {}
    
    def dump(self, id, data):
        self.files[id] = data
    
    def load(self, id):
        self._ensure_id_exists(id)
        return self.files[id]
    
    def exists(self, id):
        return id in self.files.keys()
    
    def delete(self, id):
        self._ensure_id_exists(id)
        del self.files[id]
    
    def _ensure_id_exists(self, id):
        if not self.exists(id):
            raise KeyError('id not exists')