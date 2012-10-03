class JoinStream:
    def __init__(self, streams):
        self.streams = streams
        self.currentStream = None
    
    def read(self, limit):
        readSize = 0
        import io
        result = io.BytesIO()
        while readSize < limit:
            if self.currentStream is None:
                try:
                    self.currentStream = next(self.streams)
                except StopIteration:
                    break
            remainSize = limit - readSize
            read = self.currentStream.read(remainSize)
            if not read:
                self.currentStream = None
            result.write(read)
        return result.getvalue()
    
    def close(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()