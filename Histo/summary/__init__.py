import os
from autotemp import tempdir

def _foldersummary(folder):
    #Generate each summary of files in folder
    return tuple([generatesummary(file, os.path.join(folder, file)) for file in os.listdir(folder)])

def _summaryarchive(archivetype, filename):
    with tempdir('histo-summary-') as temp:
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

_map = {
    '.rar': _rar_summary,
    '.tar': _tar_summary,
    '.tar.gz': _tar_summary,
    '.tar.bz2': _tar_summary,
    '.zip': _zip_summary,
}

def generatesummary(name, filename):
    if os.path.isdir(filename):
        return (name, _foldersummary(filename))
    else:
        for k in _map:
            if filename.endswith(k):
                return (name, _map[k](filename))
        return (name, None)