from ._reader import reader

class loader:
    def __init__(self,file):
        self._file = file
    
    def load(self):
        r = []
        while True:
            with reader(self._file) as f:
                x = f.read()
                if not x:
                    break
                r.append(x)
        return r