"""
pp4tex
preprocessor for TeX
usage: python pp4tex.py foobar.tex && platex foobat_pp.tex
"""

import sys
import os
import re

import texparse

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
PUSH_PAT = re.compile("\s*%\s*push")
POP_PAT = re.compile("\s*%\s*pop")
DEFINE_PAT = re.compile("\s*%\s*define ([^[\s]+)(?:\[(\d+)\])?\s+(.+)")
DEFINE_ML_PAT = re.compile("\s*%\s*define ([^[\s:]+)(?:\[(\d+)\])?:")
DEFINE_END_PAT = re.compile("\s*%\s*end")


class SingleLineDef(object):
    def __init__(self, body, args):
        self.body = subst(body, ns)
        if args:
            self.args = int(args)
        else:
            self.args = 0

    def eval(self, tree, i):
        if not self.args:
            return i, self.body
        
        tmp_ns = Namespace(parent=ns)
        for j in range(self.args):
            tmp_ns.set("#%d" % (j + 1), SingleLineDef(tree[i], None))
            i += 1

        return i, subst(self.body, tmp_ns)

        

class MultiLineDef(object):
    def __init__(self, body, args):
        self.body = []
        for line in body:
            is_command = process_single_line_command(line)
            if is_command:
                self.body.append(line) # don't substitute
            else:
                self.body.append(subst(line, ns))

        if args:
            self.args = int(args)
        else:
            self.args = 0

    def eval(self, tree, i):
        if not self.args:
            return i, self.body
        
        tmp_ns = Namespace(parent=ns)
        for j in range(self.args):
            tmp_ns.set("#%d" % (j + 1), (tree[i], None))
            i += 1

        body = []
        print "*"*10, ns
        for line in self.body:
            print line
            is_command = process_single_line_command(line)
            if is_command: continue
            body.expand(subst(line, tmp_ns))
        print "*"*10, ns
        return i, body

        
def traverse(tree, ns):
    new_tree = []
    i = 0
    while i < len(tree):
        item = tree[i]
        i += 1
        if isinstance(item, list):
            new_tree.append(traverse(item, ns))
        else:
            new_item = ns.get(item)
            if not new_item:
                new_tree.append(item)
            else:
                i, tokens = new_item.eval(tree, i)
                new_tree.extend(tokens)

    return new_tree


def subst(s, ns):
    if isinstance(s, str):
        tree = texparse.parse(s)
    else:
        tree = s
    new_tree = traverse(tree, ns)
    s = texparse.unparse(new_tree, True)
    return s


def assert_is_single_token(frm, lno, **kw):
    fs = texparse.parse(frm)
    if len(fs) != 1:
        raise RuntimeError(
            "line %d: key '%s' should have only one token but has %s" %
            (lno + 1, frm, fs))
            

def process_single_line_command(line, lno=0):
    "returns is_command?"
    global ns
    if not isinstance(line, str):
        raise AssertionError("str required, given %s" % line)
    if PUSH_PAT.match(line):
        ns = Namespace(parent=ns)
        return True

    if POP_PAT.match(line):
        ns = ns.parent
        return True
    
    m = DEFINE_PAT.match(line)
    if m:
        frm, arg, to =  m.groups()
        assert_is_single_token(**locals())
        ns.set(frm, SingleLineDef(to, arg))
        return True
    

def main():
    lno = 0
    while True:
        line = fi.readline()
        if not line: break
        lno += 1

        is_command = process_single_line_command(line, lno)
        if is_command: continue

        m = DEFINE_ML_PAT.match(line)
        if m:
            frm, args =  m.groups()
            assert_is_single_token(**locals())
            body = []
            while True:
                line = fi.readline()
                if not line:
                    raise RuntimeError("multiline definition '%s' is incomplete" % frm)
                lno += 1
                if DEFINE_END_PAT.match(line):
                    break
                body.append(line)
            
            ns.set(frm, MultiLineDef(body, args))
            continue

        line = subst(line, ns)
        fo.write(line)


main()
