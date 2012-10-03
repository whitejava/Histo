def initLogger(config):
    import logging
    logFile = config['LogFile']
    logFormat = config['LogFormat']
    logLevel = logging.DEBUG
    logging.basicConfig(format=logFormat, level=logLevel)
    registerGlobalLogger()
    handler = FileHandler(logFile, logFormat, logLevel)
    logger.addHandler(handler)

def registerGlobalLogger():
    import logging
    global logger
    logger = logging.getLogger()

def FileHandler(logFile, logFormat, logLevel):
    import logging
    formatter = logging.Formatter(logFormat)
    handler = logging.FileHandler(logFile)
    handler.setLevel(logLevel)
    handler.setFormatter(formatter)
    return handler
