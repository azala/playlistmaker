#!/usr/bin/env python

import plvars as plv, sys, os, subprocess
from azutils import *

if sys.argv[1] == '-in':
    cmdname = 'import'
else:
    cmdname = 'export'

lsa = len(sys.argv)

if lsa == 2:
    name = 'default'
elif lsa == 3:
    name = sys.argv[2]
else:
    sys.exit()
    
print 'Using '+cmdname+' dir "'+name+'".'
dir = opj(plv.EXPORTDIR,name)

if cmdname == 'export':
    l = ['mkdir -p "'+dir+'"',
         'cp '+opj('"'+plv.CDATAPATH+'"','*.txt')+' "'+dir+'"']
else:
    l = ['cp '+opj('"'+dir+'"','*.txt')+' "'+plv.CDATAPATH+'"']
    
for item in l:
    os.system(printret(item))