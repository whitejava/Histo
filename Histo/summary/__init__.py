def _is_directory(filename):
    import os
    return os.path.isdir(filename)

def _folder_summary(folder):
    import os
    result = []
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        result.append(generate_summary(file, path))
    return tuple(result)

def _archive_summary(archive_type, filename):
    from tempdir.tempdir import tempdir
    from ._extract_archive import extract_error
    from ._extract_archive import extract_archive
    with tempdir(prefix='histo-{}-'.format(archive_type)) as temp:
        error = None
        try:
            extract_archive(archive_type, filename, temp)
        except extract_error as e:
            error = str(e)
        return (archive_type, error, _folder_summary(temp))

def _rar_summary(filename):
    return _archive_summary('rar', filename)

def _tar_summary(filename):
    return _archive_summary('tar', filename)

def _zip_summary(filename):
    return _archive_summary('zip', filename)

_summary_table = {
    '.rar': _rar_summary,
    '.tar': _tar_summary,
    '.tar.gz': _tar_summary,
    '.tar.bz2': _tar_summary,
    '.zip': _zip_summary,
}

def generate_summary(name, filename):
    if _is_directory(filename):
        return (name, _folder_summary(filename))
    else:
        for k in _summary_table:
            if filename.endswith(k):
                return (name, _summary_table[k](filename))
        return (name, None)