def _check_type(time):
    if type(time) is not tuple:
        raise TypeError('input type error')

def _check_length(time):
    if len(time) is not 7:
        raise ValueError('input length error')

def _check_item_type(item):
    if type(item) is not int:
        raise TypeError('item type error')

def _check_item(item):
    _check_item_type(item)

def _check_items(time):
    for e in time:
        _check_item(e)

def check(time):
    _check_type(time)
    _check_length(time)
    _check_items(time)