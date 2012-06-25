def _generate_pad(padsize):
    #Pad element
    pad = bytes([padsize])
    #Duplicate element.
    pad = pad * padsize
    #Return
    return pad

def encode(input, blocksize=16):
    #Check parameter
    if blocksize < 0: raise ValueError('block size must be greater than zero.')
    #Calculate pad size.
    padsize = (blocksize-len(input)-1) % blocksize +1
    #Generate pad
    pad = _generate_pad(padsize)
    #Output
    return input + pad

def decode(input):
    #Get pad size
    padsize = input[-1]
    #Get actual pad
    actualpad = input[-padsize:]
    #Generate expected pad
    expectpad = _generate_pad(padsize)
    #Check pad
    if actualpad != expectpad: raise Exception('bad padding')
    #Strip pad
    input = input[:-padsize]
    #Return
    return input