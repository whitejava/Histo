def main():
    AdminShell().cmdloop()

import cmd
class AdminShell(cmd.Cmd):
    intro = 'Welcome to HistoAdmin shell. Type help or ? to list commands.\n'
    prompt = 'histo.admin > '
    
    def do_verifylocal(self, arg):
        ''' Verify every commitment by calculating their MD5 comparing to the MD5 in Index.'''
        with connect() as c:
            c.writeObject('VerifyLocal')
            while True:
                message = c.readObject()
                if message == 'END':
                    break
                else:
                    print(message)

def connect():
    from picklestream import PickleClient
    return PickleClient(('127.0.0.1', 3750))

if __name__ == '__main__':
    main()