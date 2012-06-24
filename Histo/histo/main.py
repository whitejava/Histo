def _load_key():
    from hex import hex
    with open('/etc/histo-key') as f:
        return hex.decode(f.read())

def _cut(string, seg):
    a = list(len(seg))
    a[0] = seg[0]
    for i in range(1,len(seg)):
        a[i] = a[i-1] + seg[i]
    a = [0] + a
    result = []
    for i in range(1,len(seg)):
        result.append(string[a[i-1]:a[i]])
    return result

def _resolve_filename(filename):
    import os
    filename = os.path.basename(filename)
    datetime = filename[:12]
    datetime = tuple([int(e)for e in _cut(datetime,[4,2,2,2,2])]+[0,0])
    name = filename[12:]
    if name.startswith('_'):
        name = name[1:]
    return datetime,name

def commit_archive(filename):
    datetime, name = _resolve_filename(filename)
    from .secure_repo import secure_repo as repo
    from summary import generate_summary
    r = repo('/var/histo', _load_key())
    summary = generate_summary(name, filename)
    r.commit_file(filename, name, summary, time = datetime)

