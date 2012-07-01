import os

__all__ = ['listfiles']

def listfiles(folder):
    #Define result
    result = []
    #Walk folder
    for dir,dirs,files in os.walk(folder):
        #List all dirs and files
        for item in dirs+files:
            #Full path
            path = os.path.join(dir, item)
            #Relative path
            path = path[len(folder)+1:]
            #Output
            result.append(path)
    #Return
    return result
