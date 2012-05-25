def commit_file(f):
    print(f)

if __name__ == '__main__':
    import sys
    files = sys.argv[1:]
    for e in files:
        commit_file(e)
