import time

_filter = None

def filter(a):
    global _filter
    _filter = a

def _matchfilter(tag):
    if _filter == None: return True
    for e in _filter:
        if tag.startswith(e):
            return True
    return False

def log(*message):
    t = '[{:13f}]'.format(time.clock())
    print(t, *message)