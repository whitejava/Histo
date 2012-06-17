class padding:
    def __init__(self, size):
        if type(size) is not int:
            raise TypeError('size type error')
        if size not in range(1, 256):
            raise ValueError('size value error')
        self._size = size
    
    def encode(self, b):
        if type(b) is not bytes:
            raise TypeError('encode input type error')
        append_size = (-len(b)-1) % self._size + 1
        return b + bytes([append_size] * append_size)
    
    def decode(self, b):
        if type(b) is not bytes:
            raise TypeError('decode input type error')
        if len(b) % self._size is not 0:
            raise ValueError('decode input is not padding')
        if len(b) is 0:
            raise ValueError('decode input is empty')
        append_size = b[-1]
        if append_size not in range(1, self._size + 1):
            raise ValueError('padding value error')
        padding = b[-append_size:]
        for e in padding:
            if e is not append_size:
                raise ValueError('padding value error')
        return b[:-append_size]