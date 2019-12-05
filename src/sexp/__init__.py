
import re
 

dbg = False

 
term_regex = r'''(?mx)
    \s*(?:
        (?P<brackl>\()|
        (?P<brackr>\))|
        (?P<hex>0[xX][0-9a-fA-F]+)|
        (?P<num>\-?\d+\.\d+|\-?\d+)|
        (?P<sq>"[^"]*")|
        (?P<s>[^(^)\s]+)
       )'''
 

def parse_sexp(sexp):
    stack = []
    out = []
    if dbg: print("%-6s %-14s %-44s %-s" % tuple("term value out stack".split()))
    for termtypes in re.finditer(term_regex, sexp):
        term, value = [(t,v) for t,v in termtypes.groupdict().items() if v][0]
        if dbg: print("%-7s %-14s %-44r %-r" % (term, value, out, stack))
        if term == 'brackl':
            stack.append(out)
            out = []
        elif term == 'brackr':
            assert stack, "Trouble with nesting of brackets"
            tmpout, out = out, stack.pop(-1)
            out.append(tmpout)
        elif term == 'hex':
            out.append(value)
        elif term == 'num':
            v = float(value)
            if v.is_integer(): v = int(v)
            out.append(v)
        elif term == 'sq':
            out.append(value[1:-1])
        elif term == 's':
            out.append(value)
        else:
            raise NotImplementedError
    assert not stack, "Trouble with nesting of brackets"
    return out[0]
 

def print_sexp(exp):
    out = ''
    if type(exp) == type([]):
        out += '(' + ' '.join(print_sexp(x) for x in exp) + ')'
    elif type(exp) == type('') and re.search(r'[\s()]', exp):
        out += '"%s"' % repr(exp)[1:-1].replace('"', '\"')
    else:
        out += '%s' % exp
    return out


def read_sexp(file_name):
    line = ""
    rtl_exprs = []

    with open(file_name, "r") as in_file:
        func_name = ""
        # Read past the garbage at the beginning
        line = in_file.readline()
        while line[0] != '(' and line != "":
            line = line.lower().split()
            if "function" in line:
                if "void" in line:
                    func_name = line[line.index("void") + 1].split("(")[0]
                else:
                    func_name = line[line.index("function") + 1].split("(")[0]
            line = in_file.readline()

        while line != "":
            line = line.replace('[', '(').replace(']', ')')
            try:
                rtl_exprs.append(parse_sexp(line))
                line = ""
            except AssertionError:
                pass

            line += in_file.readline()
    
    return func_name, rtl_exprs
