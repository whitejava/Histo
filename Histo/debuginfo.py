class DebugInfo:
    def __init__(self, message):
        self.message = message
        self.result = ''
    
    def __enter__(self):
        import logging
        logging.debug('[ %s' % self.message)
        return self
        
    def __exit__(self, et, ev, trace):
        import logging
        logging.debug(' ]%s' % self.result)