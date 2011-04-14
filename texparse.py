"""
texparse.py: parse TeX line
"""
from string import ascii_letters
SPACES = " \t"
def spaces(s, i):
    r"""
    >>> spaces("  a", 0)
    ('  ', 2)
    """
    start = i
    while s[i] in SPACES:
        i += 1
    return (s[start:i], i)


def term(s, i):
    r"""
    >>> term("aaa", 0)
    ('aaa', 3)
    >>> term("aaa  ", 0)
    ('aaa', 3)
    >>> term(r"aaa\aaa", 0)
    ('aaa', 3)
    >>> term(r"\aaa aaa", 0)
    ('\\aaa', 4)
    >>> term(r"\{aaa", 0)
    ('{', 2)
    """
    start = i
    escaped = False # T when \ appeared
    while i < len(s):
        if s[i] in SPACES:
            break
        elif s[i] in "{}":
            if escaped:
                return (s[i], i + 1)
            break
        elif s[i] == "\\":
            if i != start:
                break
            escaped = True
        elif s[i] in ascii_letters:
            if escaped: escaped = False
        else:
            if i != start: break
            i += 1
            break

        i += 1
    return (s[start:i], i)


def brace(s, i):
    assert s[i] == "{"
    tokens, i = parse_tokens(s, i + 1)
    return (tokens, i)


def parse_tokens(s, i):
    tokens = []
    while i < len(s):
        if s[i] in SPACES:
            tok, i = spaces(s, i)
            tokens.append(tok)
        elif s[i] == "{":
            tok, i = brace(s, i)
            tokens.append(tok)
        elif s[i] == "}":
            i += 1
            break
        else:
            tok, i = term(s, i)
            tokens.append(tok)
            
    return (tokens, i)


def parse(s, i=0):
    r"""
    >>> parse("hoge")
    ['hoge']
    >>> parse(r"\ho\ge")
    ['\\ho', '\\ge']
    >>> parse(r"  \hoge")
    ['  ', '\\hoge']
    >>> parse(r"a{ho ge}ga")
    ['a', ['ho', ' ', 'ge'], 'ga']
    >>> parse(r"\{aaa\}")
    ['{', 'aaa', '}']
    >>> parse(r"\frac{x^2}{2} + x")
    ['\\frac', ['x', '^', '2'], ['2'], ' ', '+', ' ', 'x']

    """
    tokens, i = parse_tokens(s, 0)
    return tokens

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
