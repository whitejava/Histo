def main():
    root = 'G:\\test-summary'
    from histo.summary import generateSummary
    summary = generateSummary('TestSummary', root)
    from pprint import pprint
    pprint(summary, indent=4, width=1)
    
if __name__ == '__main__':
    main()