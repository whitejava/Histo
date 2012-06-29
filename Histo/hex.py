def encode(b):
    return ''.join(['{:02x}'.format(e) for e in b])

def decode(a):
    return bytes([int(a[i:i+2],16) for i in range(0,len(a),2)])