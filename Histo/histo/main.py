def _load_key():
    from hex import hex
    with open('/etc/histo-key') as f:
        return hex.decode(f.read())

def _cut(string, seg):
    a = list(len(seg))
    a[0] = seg[0]
    for i in range(1,len(seg)):
        a[i] = a[i-1] + seg[i]
    a = [0] + a
    result = []
    for i in range(1,len(seg)):
        result.append(string[a[i-1]:a[i]])
    return result

def _resolve_filename(filename):
    import os
    filename = os.path.basename(filename)
    datetime = filename[:12]
    datetime = tuple([int(e)for e in _cut(datetime,[4,2,2,2,2])]+[0,0])
    name = filename[12:-4]
    if name.startswith('_'):
        name = name[1:]
    return datetime,name

def commit_archive(filename):
    datetime, name = _resolve_filename(filename)
    from .secure_repo import secure_repo as repo
    from summary import generate_summary
    r = repo('/var/histo', _load_key())
    summary = generate_summary(name, filename)
    r.commit_file(filename, name, summary, time = datetime)
    
class my_repo:
    def __init__(self):
        from .secure_repo import secure_repo as repo
        self._repo = repo(_load_key())
    
    def commit_file(self, filename, name, time = None):
        from summary import generate_summary
        summary = generate_summary(name, filename)
        self._repo.commit_file(filename, name, summary, time)
    
    def __enter__(self):
        self._repo.__enter__()
        return self
    
    def __exit__(self,*k):
        self._repo.__exit__(*k)

class logger:
    def write(self, message):
        import time
        print('[{:8.2f}]{}'.format(time.clock(), message))

from socketserver import StreamRequestHandler

def transfer_stream(input, output, size, chunk_size = 128*1024):
    while size:
        read = input.read(chunk_size)
        size -= len(read)
        output.write(read)

class commit_handler(StreamRequestHandler):
    def handle(self):
        from struct import unpack
        log.write('on request')
        name = unpack('i', self.rfile.read(4))
        log.write('name len {}'.format(name))
        name = self.rfile.read(name)
        name = str(name, 'utf8')
        log.write('name {}'.format(name))
        time = unpack('i', self.rfile.read(4))
        log.write('time len {}'.format(time))
        if time == 0:
            time = None
        else:
            time = tuple([int(self.rfile.read(4))for _ in range(time)])
        log.write('time {}'.format(time))
        size = unpack('q', self.rfile.read(8))
        log.write('size {}'.format(size))
        log.write('receiving data')
        from tempdir.tempdir import tempdir
        with tempdir(prefix='') as temp:
            import os
            filename = os.path.join(temp,'data')
            with open(filename, 'wb') as f:
                transfer_stream(self.rfile, f, size)
            log.write('commiting')
            with my_repo() as repo:
                repo.commit_file(filename, name, time)
            log.write('ok')

log = logger()

def server():
    log.write('starting server')
    from socketserver import TCPServer
    server = TCPServer(('0.0.0.0',13750), commit_handler)
    log.write('listening')
    server.serve_forever()

if __name__ == '__main__':
    server()