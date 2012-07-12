from datetime import datetime

def totuple(t):
    '''
    Translate a python datetime object into tuple object.
    '''
    return (t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond)

def nowtuple():
    return totuple(datetime.now())