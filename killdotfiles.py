#!/usr/bin/env python

import plvars as plv, os

l = ['.fseventsd',
     '.Spotlight-V100',
     '.Trashes']
count = 0

for fn in l:
    fulln = os.path.join(plv.ROOTDIR,fn)
    if os.path.exists(fulln):
        count += 1
        s = 'rm -rf "'+os.path.join(plv.ROOTDIR,fn)+'"'
        os.system(s)

if count > 0:
    print 'Killed '+`count`+' apple dotfiles.'