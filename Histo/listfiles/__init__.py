def listfiles(folder):
    import os
    result = []
    for e in os.walk(folder):
        for e2 in e[1] + e[2]:
            result.append(os.path.join(e[0],e2)[len(folder):])
    return result
