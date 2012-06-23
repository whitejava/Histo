def _get_filename(pathname):
    import os
    return pathname.split(os.path.sep)[-1]

def _get_extension(pathname):
    filename = _get_filename(pathname)
    split = filename.split('.')
    if len(split) == 1:
        return ''
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
    import os
    result = []
    for files in os.listdir(folder):
        for file in files:
            path = os.path.join(folder, file)
            result.append(generate_summary(file, path))
    return tuple(result)

def _is_directory(filename):
    import os
    return os.path.isdir(filename)

def _rar_summary(filename):
    from tempdir.tempdir import tempdir
    with tempdir(prefix='histo-rar-') as temp:
        error = None
        try:
            _extract_rar(filename, temp)
        except Exception as e:
            error = e.args[0]
            if error.startswith('rar return error code '):
                pass
        return ('rar', error, _folder_summary(temp))

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

def generate_summary(name, filename):
    if _is_directory(filename):
        return (name, _folder_summary(filename))
    else:
        extension = _get_extension(filename).lower()
        if extension in _dispatch_table:
            return (name,_dispatch_table[extension](filename))
        return (name, None)