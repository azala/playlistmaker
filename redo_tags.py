import os, shutil, sys
import plvars as plv

def decoded(lines):
    ret = {}
    boo = len(sys.argv) >= 2 and '-r' in sys.argv
    for l in lines:
        ls = l.decode('utf').split('\t')
        fn = ls[0]
        #fn = l.decode('utf')[:-2]
        k = fn.rpartition('\\')[2].lower()
        #k = ls[1][:-2]
        if k in ret and boo:
            print k
            print '  '+ret[k]
            print '  '+fn
            i = raw_input('Move which one?\n>> ')
            if i == '1':
                shutil.move(ret[k], 'E:\\moved')
                print 'Moved 1.'
            elif i == '2':
                shutil.move(fn, 'E:\\moved')
                print 'Moved 2.'
        ret[k] = fn
    return ret

f = open(plv.DIRFILLPATH, 'rb')
fdict = decoded(f.readlines())
f.close()

g = open(plv.tagfile, 'rb')
glist = map(lambda x: list(x.decode('utf').partition('\t')), g.readlines())
g.close()
ret = []
for gl in glist:
    glrp = gl[0].rpartition('\\')[2].lower()
    if glrp in fdict and gl[0] != fdict[glrp]:
        try:
            print 'Detected move: '+glrp
        except:
            pass
        gl[0] = fdict[glrp]
    ret += gl
print 'Writing tags...'
g = open(plv.tagfile, 'wb')
g.writelines(map(lambda x: ''.join(x).encode('utf'), ret))
g.close()
print 'Done!\n'
