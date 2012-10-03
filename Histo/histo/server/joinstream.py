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
            readSize += len(read)
        return result.getvalue()
    
    def close(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *k):
        self.close()

if __name__ == '__main__':
    from pclib import copystream
    with open('D:\\1.txt', 'rb') as a:
        with open('D:\\2.txt', 'rb') as b:
            with open('D:\\12.txt', 'wb') as c:
                copystream(JoinStream(iter([a,b])), c, chunksize=2)