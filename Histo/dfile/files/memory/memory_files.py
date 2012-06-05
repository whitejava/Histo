from _writer import writer as bytes_writer
from _reader import reader as bytes_reader

class memory_files:
    def __init__(self):
        self.library = {}
    
    def open_for_write(self, n):
        self.library[n] = bytearray()
        return bytes_writer(self.library, n)
    
    def open_for_read(self, n):
        return bytes_reader(self.library[n])