from ._decrypt_error import decrypt_error

class test_cipher:
    def encrypt(self,b):
        return b'a' + b + b'b'
    
    def decrypt(self,b):
        if len(b) < 2:
            raise decrypt_error()
        b = bytes(b)
        print(b)
        if b[0] != ord(b'a') or b[-1] != ord(b'b'):
            raise decrypt_error()
        return b[1:-1]