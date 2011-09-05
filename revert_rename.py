#!/usr/bin/env python

import os, sys, azutils, rename

def main():
    if len(sys.argv) != 3:
        print 'Need 2 args.'
        exit()
    oldfn = sys.argv[1]
    newfn = sys.argv[2]
    a = azutils.readToSplitList(oldfn)
    b = azutils.readToSplitList(newfn)
    func = lambda x: (rename.standard_rename_op(x[0]), x[0])
    c = map(func, a)
    d = map(func, b)
    l = []
    for cc in c:
        for dd in d:
            if cc[0] == dd[0] and cc[1] != dd[1]:
                l.append((cc[1],dd[1]))
                break
    print `len(l)`+' moves to be made.'
    for k in l:
        os.rename(k[0],k[1])
        #print k[0]+'\t'+k[1]
    
if __name__ == "__main__":
    main()