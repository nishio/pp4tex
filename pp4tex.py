"""
pp4tex
preprocessor for TeX
usage: python pp4tex.py foobar.tex && platex foobat_pp.tex

"""
import sys
import os
import re

target = sys.argv[1]
path, fn = os.path.split(target)
trunk, ext = os.path.splitext(fn)

target = os.path.join(path, "%s.%s" % (trunk, "tex"))
outfile = os.path.join(path, "pp_%s.%s" % (trunk, "tex"))
fi = open(target)
fo = open(outfile, "w")

class Namespace(dict):
    def __init__(self, parent=None, **kw):
        super(Namespace, self).__init__(**kw)
        self.parent = parent

    def get(self, key):
        v = super(Namespace, self).get(key)
        if not v:
            if not self.parent:
                return None
            v = self.parent.get(key)
        return v

    def set(self, key, value):
        self[key] = value

ns = Namespace()
top = ns

PUSH_PAT = re.compile("\s*%\s*push")
POP_PAT = re.compile("\s*%\s*pop")
DEFINE_PAT = re.compile("\s*%\s*define ([^\s]+)\s+(.*)")

def subst(s, ns):
    while ns != None:
        for k in ns:
            s = s.replace(k, ns[k])
        ns = ns.parent
    return s

for lno, line in enumerate(fi):
    if PUSH_PAT.match(line):
        ns = Namespace(parent=ns)
        continue
    if POP_PAT.match(line):
        ns = ns.parent
        continue
    m = DEFINE_PAT.match(line)
    if m:
        frm, to =  m.groups()
        ns.set(frm, subst(to, ns))
        continue

    line = subst(line, ns)
    fo.write(line)

