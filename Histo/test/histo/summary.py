def main():
    #testSimplify()
    testSummary()

def testSimplify():
    summary = [[1,5,9,5,[1,2,3,4,2,4,3],2,5,[1,2,5,6,2,3]],2,[5,[9,8,5,2,3,4],7,8],4]
    from histo.server.summary import simplify
    summary = simplify(summary, 10)
    from pprint import pprint
    pprint(summary, indent=4, width=1)

def testSummary():
    root = 'G:\\test-summary'
    from histo.server.summary import generateSummary
    summary = generateSummary('TestSummary', root)
    from pprint import pprint
    pprint(summary, indent=4, width=1)
    
if __name__ == '__main__':
    main()