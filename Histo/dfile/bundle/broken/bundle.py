class bundle:
    def __init__(self, base, broken):
        self._base = base
        self._broken = broken
    
    def dump(self,n,b):
        self._ensure_not_broken(n)
        return self._base.dump(n,b)
    
    def load(self,n):
        self._ensure_not_broken(n)
        return self._base.load(n)
    
    def exists(self,n):
        self._ensure_not_broken(n)
        return self._base.exists(n)
    
    def _ensure_not_broken(self,n):
        for e in self._broken:
            if e == n:
                raise IOError('broken')