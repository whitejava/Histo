def _run_extract_command(command):
    from subprocess import Popen, PIPE
    proc = Popen(command, stdin=PIPE)
    proc.stdin.close() # prevent got blocked when should enter password.
    exitcode = proc.wait()
    if exitcode != 0:
        raise extract_error(exitcode)

def _get_extract_command(archive_type, filename, target):
    table = {'rar': ['rar','x',filename,target+'/'],
             'tar': ['tar', '-xf', filename, '-C', target],
             'zip': ['unzip', filename, '-d', target]}
    return table[archive_type]

class extract_error(SystemError):
    def __init__(self, exitcode):
        self.exitcode = exitcode
    
    def __str__(self):
        return 'extract error {}'.format(self.exitcode)

def extract_archive(type, filename, target):
    command = _get_extract_command(type, filename, target)
    _run_extract_command(command)