#!/usr/bin/env python

import os, shutil, sys
import plvars as plv
import rename
from plutil import *

def decoded(lines):
    ret = {}
    boo = len(sys.argv) >= 2 and '-r' in sys.argv
    for ls in lines:
        #ls = l.decode('utf').split('\t')
        fn = ls[0]
        k = fn.rpartition(plv.cSep)[2].lower()
        if k in ret and boo:
            print str(k)
            print '  '+ret[k]
            print '  '+fn
            i = raw_input('Move which one?\n>> ')
            if i == '1':
                shutil.move(ret[k], plv.MOVEDPATH)
                print 'Moved 1.'
            elif i == '2':
                shutil.move(fn, plv.MOVEDPATH)
                print 'Moved 2.'
        ret[k] = fn
    return ret

f = open(plv.DIRFILLPATH, 'rb')
#l = list(map(lambda x: x.decode('utf').split('\t'), f.readlines()))
l = list(map(lambda x: x.split('\t'), clean(fread(plv.DIRFILLPATH))))
kmdict = shortNameToFullDict(list(map(lambda x: x[0], l)))
fdict = decoded(l)
f.close()

g = open(plv.tagfile, 'rb')
glist = map(lambda x: list(x.decode('utf').partition('\t')), g.readlines())
g.close()

ret = []
for gl in glist:
    gl[0] = gl[0].replace('\\',plv.cSep)
    glShort = unorm(gl[0].rpartition(plv.cSep)[2].lower())
    if glShort in kmdict and gl[0] not in kmdict[glShort]:
        try:
            print 'Detected move: '+glShort
        except:
            print plv.cBadStr
            pass
        gl[0] = kmdict[glShort][0]
    ret += gl
print 'Writing tags...'
g = open(plv.tagfile, 'wb')
g.writelines(map(lambda x: ''.join(x).encode('utf'), ret))
g.close()
print 'Writing ratings...'
h = clean(fread(plv.ratingFile))
dst = []
#backslash check
try:
    backslashes = ('\\' in h[0])
except:
    backslashes = False
#
for ratingLine in h:
    if backslashes:
        ratingLine = ratingLine.replace('\\',plv.cSep)
    pt = ratingLine.partition('\t')
    short = unorm(pt[0].rpartition(plv.cSep)[2].lower())
    if short not in kmdict:
        print short
    dst.append(kmdict[short][0]+'\t'+pt[2])
dst = map(unorm, dst)
fwrite(unclean(dst), plv.ratingFile)
print 'Done!\n'
