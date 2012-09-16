#coding=utf8

def main():
    import sys
    return main2(*sys.argv[1:])

def main2(action, configFilePath):
    config = loadConfig(configFilePath)
    return main3(action, config['Histo'])

def loadConfig(configFilePath):
    import json
    with open(configFilePath, 'r', encoding='utf8') as f:
        return json.load(f)

def main3(action, config):
    initLogging(config['Log'])
    main4(action, config)

def initLogging(config):
    import logging
    logging.basicConfig(format=config['Format'], datefmt=config['DateFormat'], level=logging.DEBUG, style='$')

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