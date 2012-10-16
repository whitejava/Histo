def main():
    sourceFolder = 'E:\\git\\Histo\\Histo'
    targetFolder = 'F:\\Histo\\python'
    removeFolder(targetFolder)
    copyFolder(sourceFolder, targetFolder)

def removeFolder(folder):
    try:
        import shutil
        shutil.rmtree(folder)
    except:
        pass

def copyFolder(source, target):
    import shutil
    shutil.copytree(source, target)

if __name__ == '__main__':
    main()