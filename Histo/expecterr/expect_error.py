class expect_error:
    def __init__(self, message):
        self._message = message
    
    def __enter__(self):
        pass
    
    def __exit__(self, t, value, trace):
        if value == None:
            raise Exception('expect exception')
        if len(value.args) < 1:
            raise Exception('exception has no message')
        if value.args[0] != self._message:
            raise Exception('unexpected message')
        return True