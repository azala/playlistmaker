#!/usr/bin/env python

import plvars as plv, sys, os, subprocess
from azutils import *

if not os.path.exists(plv.ROOTDIR):
    print 'IPOD doesn\'t exist.'
    sys.exit(0)

if sys.argv[1] == '-in':
    cmdname = 'import'
else:
    cmdname = 'export'

lsa = len(sys.argv)
silentMode = lsa >= 3 and '-s' in sys.argv
if silentMode:
    sys.argv.remove('-s')
    lsa -= 1

if lsa == 2:
    name = 'default'
elif lsa == 3:
    name = sys.argv[2]
else:
    sys.exit()
 
if not silentMode:   
    print 'Using '+cmdname+' dir "'+name+'".'
dir = opj(plv.EXPORTDIR,name)

if cmdname == 'export':
    l = ['mkdir -p "'+dir+'"',
         'cp '+opj('"'+plv.CDATAPATH+'"','*.txt')+' "'+dir+'"']
else:
    l = ['cp '+opj('"'+dir+'"','*.txt')+' "'+plv.CDATAPATH+'"']
    
for item in l:
    if silentMode:
        s = item
    else:
        s = printret(item)
    os.system(s)