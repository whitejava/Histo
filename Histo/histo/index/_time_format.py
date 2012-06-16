def _check_type(time):
    if type(time) is not tuple:
        raise TypeError('input type error')

def _check_length(time):
    if len(time) is not 7:
        raise ValueError('input length error')

def check(time):
    _check_type(time)
    _check_length(time)