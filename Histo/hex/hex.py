def encode(b):
    if type(b) is not bytes:
        raise TypeError('input type error')
    return ''.join(['{:02x}'.format(e) for e in b])

def decode(a):
    if type(a) is not str:
        raise TypeError('input type error')
    if len(a) % 2 is not 0:
        raise ValueError('input length odd')
    return bytes([int(a[i:i+2],16) for i in range(0,len(a),2)])