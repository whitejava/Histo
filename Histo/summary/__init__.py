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

def generate_summary(filename):
    extension = _get_extension(filename)
    