class Codes:
    @staticmethod
    def simplify(codes):
        result = []
        while codes:
            maxContinuous = findMaxContinuous(codes)
            if maxContinuous == 1:
                result.append(codes[0])
            else:
                result.append((codes[0], codes[0] + maxContinuous - 1))
            del codes[:maxContinuous]
        return result
    
    @staticmethod
    def walk(x):
        for e in x:
            if type(e) is tuple:
                for f in range(e[0], e[1]):
                    yield f
            else:
                yield e

def findMaxContinuous(codes):
    for i in range(len(codes)):
        if codes[i] - codes[0] != i:
            return i + 1
    return len(codes)
