class expect_error:
    def __init__(self, message):
        self._message = message
    
    def __enter__(self):
        pass
    
    def __exit__(self, t, value, trace):
        if value == None:
            raise Exception('expect exception')
        message = str(value)
        if message != self._message:
            raise Exception('unexpected message: {}'.format(message))
        return True