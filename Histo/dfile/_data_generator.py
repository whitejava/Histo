class data_generator:
    def __init__(self):
        self.pointer = 0
    
    def seek(self, pos):
        self.pointer = pos
    
    def read(self, count):
        start = self.pointer
        self.pointer += count
        end = self.pointer
        return self._get_data(start, end)
    
    def _get_data(self, start, end):
        return bytes([e % 256 for e in range(start, end)])
