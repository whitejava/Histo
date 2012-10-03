#encoding: utf8

def main():
    initLogger()
    while True:
        randomAction()

def initLogger():
    import logging
    format2 = '%(asctime)s %(thread)08d %(message)s'
    logging.basicConfig(format=format2, level=logging.DEBUG)
    from pclib import timetext
    handler = logging.FileHandler('D:\\%s.log' % timetext())
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(format2))
    global logger
    logger = logging.getLogger()
    logger.addHandler(handler)

def randomAction():
    actions = [testCommit, testBrowse]
    import random
    random.choice(actions)()

def testCommit():
    logger.debug('[ Test Commit')
    root = 'G:\\test-server'
    import os
    if not os.listdir(root):
        logger.debug('Nothing to commit')
    else:
        logger.debug('[ Random file')
        file = randomFile(root)
        logger.debug(' ]%s' % file)
        from histo.commit import commit
        logger.debug('[ Commit')
        commit(file)
        logger.debug(' ]')
    logger.debug(' ]')

def randomFile(root):
    import os
    import random
    return os.path.join(root, random.choice(os.listdir(root)))

def testBrowse():
    logger.debug('[ Test browse')
    logger.debug('[ Random keywords')
    keywords = randomKeywords()
    logger.debug(' ]%s' % keywords)
    result = testSearch(keywords)
    if result:
        import random
        testDownload(random.choice(result))
        logger.debug(' ]')
    else:
        logger.debug('Nothing to download')
    
def randomKeywords():
    keywords = ['']+list('我知道就算大雨让这座城市颠倒')
    import random
    return random.choice(keywords)

def testSearch(keywords):
    logger.debug('[ Test search')
    logger.debug('[ Search')
    from histo.browser import search
    result = search(keywords)
    logger.debug(' ]%d' % len(result))
    for e in result:
        logger.debug('%d %s' % (e['CommitID'], e['Name']))
    logger.debug(' ]')
    return result
    
def testDownload(commit):
    logger.debug('[ Test download')
    from histo.browser import download
    download(commit, 'D:\\histo-extract')
    logger.debug(' ]')

if __name__ == '__main__':
    main()