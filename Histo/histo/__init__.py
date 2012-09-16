#coding=utf8

def main():
    import sys
    return main2(sys.argv[1:])

def main2(action, configFilePath):
    config = loadConfig(configFilePath)
    return main3(action, config)

def loadConfig(configFilePath):
    from configparser import ConfigParser
    return ConfigParser().read(configFilePath, 'utf8')

def main3(action, config):
    initLogging(config)
    main4(action, config)

def initLogging(config):
    config = config['Histo.Log']
    import logging
    logging.basicConfig(format=config['Format'], datefmt=config['DateFormat'], level=logging.DEBUG)

def main4(action, config):
    try:
        return getActionTable()[action](config)
    finally:
        import logging
        logging.shutdown()

def getActionTable():
    return {'RunServer': runServer,
            'RunBrowser': runBrowser,
            'Commit': commit,}

def runServer(config):
    from histo.server import main as serverMain
    return serverMain(config)

def runBrowser(config):
    pass

def commit(config):
    pass

if __name__ == '__main__':
    main()