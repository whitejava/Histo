from subprocess import Popen, STDOUT, PIPE

def quietcall(commands):
    proc = Popen(commands, stdin = None, stderr = STDOUT, stdout = PIPE)
    while True:
        try:
            proc.communicate()
        except ValueError as e:
            if e.args[0] == 'I/O operation on closed file':
                break
            else:
                raise
    return proc.wait()