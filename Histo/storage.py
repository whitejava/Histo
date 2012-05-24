class FileStorage:
    def __init__(self,file):
        self._file = file
    def exist(self):
        from os.path import isfile
        return isfile(self._file)
    def load(self):
        import pickle
        return pickle.load(self._file)
    def save(self,o):
        import pickle
        pickle.dump(o, self._file)

class PrintStorage:
    def exist(self):
        return False
    def load(self):
        raise IOError
    def save(self,o):
        print(o)
