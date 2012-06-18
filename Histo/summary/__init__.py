def _get_filename(pathname):
    import os
    return pathname.split(os.path.sep)[-1]

def _get_extension(pathname):
    filename = _get_filename(pathname)
    split = filename.split('.')
    if len(split) == 1:
        return None
    else:
        return split[-1]

def _extract_rar(filename, target):
    from subprocess import Popen, PIPE
    proc = Popen(['rar', 'x', filename, target+'/'], stdin=PIPE)
    proc.stdin.close() # prevent got blocked when should enter password.
    return_code = proc.wait()
    if return_code != 0:
        raise SystemError('rar return error code {}'.format(return_code))

def _folder_summary(folder):
    raise Exception('no impl')

def _rar_summary(filename):
    from tempdir.tempdir import tempdir
    with tempdir('histo-rar-') as temp:
        _extract_rar(filename, temp)
        return _folder_summary(temp)

def _tar_summary(filename):
    pass

def _zip_summary(filename):
    pass

def _bz2_summary(filename):
    pass

def _txt_summary(filename):
    pass

_dispatch_table = {
    'rar': _rar_summary,
    'tar': _tar_summary,
    'zip': _zip_summary,
    'bz2': _bz2_summary,
    'txt': _txt_summary,
}

def generate_summary(filename):
    extension = _get_extension(filename).lower()
    if extension in _dispatch_table:
        return _dispatch_table[extension](filename)