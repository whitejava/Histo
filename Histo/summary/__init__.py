def _is_directory(filename):
    import os
    return os.path.isdir(filename)

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

def _folder_summary(folder):
    import os
    result = []
    for files in os.listdir(folder):
        for file in files:
            path = os.path.join(folder, file)
            result.append(generate_summary(file, path))
    return tuple(result)

def _archive_summary(filename, archive_type):
    from tempdir.tempdir import tempdir
    from ._extract_archive import extract_error
    from ._extract_archive import _extract_archive
    with tempdir(prefix='histo-{}-'.format(archive_type)) as temp:
        error = None
        try:
            _extract_archive(archive_type, filename, temp)
        except extract_error as e:
            error = str(e)
        return (archive_type, error, _folder_summary(temp))

def _archive_summarier(type):
    return lambda x:_archive_summary(x,type)

def _txt_summary(filename):
    pass

_summary_table = {
    'rar': _archive_summarier('rar'),
    'tar': _archive_summarier('tar'),
    'zip': _archive_summarier('zip'),
    'bz2': _archive_summarier('bz2'),
    'txt': _txt_summary,
}

def generate_summary(name, filename):
    if _is_directory(filename):
        return (name, _folder_summary(filename))
    else:
        extension = _get_extension(filename).lower()
        if extension in _summary_table:
            return (name,_summary_table[extension](filename))
        return (name, None)