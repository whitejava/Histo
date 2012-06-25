def _cut(string, seg):
    a = [None]*len(seg)
    a[0] = seg[0]
    for i in range(1,len(seg)):
        a[i] = a[i-1] + seg[i]
    a = [0] + a
    result = []
    for i in range(1,len(a)):
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
    from io import BytesIO
    from struct import pack
    import socket
    import os
    datetime, name = _resolve_filename(filename)
    name = name.encode('utf8')
    b = BytesIO()
    b.write(pack('i',len(name)))
    b.write(name)
    b.write(pack('i',len(datetime)))
    for e in datetime:
        b.write(pack('i',e))
    b.write(pack('q',os.path.getsize(filename)))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('192.168.2.4', 13750))
    s.sendall(b.getvalue())
    with open(filename,'rb') as f:
        while True:
            read = f.read(128*1024)
            if not read:
                break
            s.sendall(read)