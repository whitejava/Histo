import time

def log(*message):
    t = '[{:13f}]'.format(time.clock())
    print(t, *message)