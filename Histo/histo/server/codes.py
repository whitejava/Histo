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
                for f in range(e[0], e[1]+1):
                    yield f
            else:
                yield e

def findMaxContinuous(codes):
    for i in range(len(codes)):
        if codes[i] - codes[0] != i:
            return i + 1
    return len(codes)

def openCodesAsStreams(bundle, codes, formatter):
    for e in Codes.walk(codes):
        with bundle.open(formatter(e), 'rb') as f:
            yield f
            
def openCodesAsSingleStream(bundle, codes, formatter):
    from histo.server.joinstream import JoinStream
    streams = openCodesAsStreams(bundle, codes, formatter)
    return JoinStream(streams)

if __name__ == '__main__':
    from histo.bundle import Local
    bundle = Local('D:\\histo-server\\data\\cache')
    stream = openCodesAsSingleStream(bundle, [0,1,2,3,4], 'data-{:08d}'.format)
    from pclib import copystream
    with open('D:\\output.rar', 'wb') as f:
        copystream(stream, f)