def _tab(lines):
    return ['    '+e for e in lines]

def _indent_raw(input):
    if type(input) in (tuple,list):
        result = ['(']
        for e in input:
            result.extend(_tab(_indent_raw(e)))
            result[-1] += ','
        result.append(')')
        return result
    else:
        return [repr(input)]

def indent(input):
    return '\n'.join(_indent_raw(input))
