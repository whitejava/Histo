_keys = ['version','commit_time','name','last_modify','range','files']

def _check_type(commit):
    if type(commit) is not tuple:
        raise TypeError('input type error')

def _check_length(commit):
    if len(commit) is not len(_keys):
        raise ValueError('input length error')

def _check_item_type(item):
    if type(item) is not tuple:
        raise TypeError('item type error')

def _check_item_types(commit):
    for e in commit:
        _check_item_type(e)

def _check_item_length(item):
    if len(item) is not 2:
        raise ValueError('item length error')

def _check_item_lengths(commit):
    for e in commit:
        _check_item_lengths(e)

def _check_item_names(commit):
    for a,b in zip(commit, _keys):
        if a != b:
            raise ValueError('item name error')

def _check_version(version):
    if type(version) is not int:
        raise ValueError('version type error')
    if version is not 0:
        raise ValueError('version value error')

def _check_time(time):
    from . import _time_format
    _time_format.check(time)

def _check_name(name):
    if type(name) is not str:
        raise TypeError('name type error')

def _check_last_modify(last_modify):
    _check_time(last_modify)

def _check_range_type(range):
    if type(range) is not tuple:
        raise TypeError('range type error')

def _check_range_length(range):
    if len(range) is not 2:
        raise ValueError('range length error')

def _check_range_value(range):
    if range[0] > range[1]:
        raise ValueError('range value error')

def _check_range(range):
    _check_range_type(range)
    _check_range_length(range)
    _check_range_value(range)

def _check_summary(summary):
    if type(summary) is not str:
        raise TypeError('summary type error')

def _check_items(commit):
    steps = [_check_version,
        _check_time,
        _check_name,
        _check_last_modify,
        _check_range,
        _check_summary]
    for i,check in enumerate(steps):
        check(commit[i])

def check(commit):
    steps = [
        _check_type,
        _check_length,
        _check_item_types,
        _check_item_lengths,
        _check_item_names,
        _check_items]
    for e in steps:
        e(commit)