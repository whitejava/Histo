def main():
    import logging
    global logger
    logging.basicConfig(format='%(asctime)s %(thread)08d %(message)s', level=logging.DEBUG)
    logger = logging.getLogger()
    q = Queue()
    for _ in range(500):
        TestThreadTaskQueue(q).start()

def Queue():
    from histo.bundle.buffer import TaskQueue
    from pclib import timetext
    return TaskQueue('D:\\%s-test-task-queue' % timetext())

def TestThreadTaskQueue(q):
    from threading import Thread
    return Thread(target=testQueue, args=(q,))
    
def testQueue(q):
    while True:
        randomAction(q)

def randomAction(q):
    actions = [testAppend, testFetch]
    import random
    random.choice(actions)(q)

def testAppend(q):
    import random
    d = random.randrange(10)
    logger.debug('[ + %s' % d)
    q.append(d)
    logger.debug(' ]+ %s' % d)

def testFetch(q):
    import random
    logger.debug('[ -')
    fetchId, x = q.fetch()
    logger.debug(' ]- %s' % x)
    if random.choice([True, False]):
        logger.debug('Feedback True')
        q.feedBack(fetchId, True)
    else:
        logger.debug('Feedback False')
        q.feedBack(fetchId, False)

if __name__ == '__main__':
    main()