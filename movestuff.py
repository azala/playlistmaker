#!/usr/bin/env python

import os, sys
import plvars as plv

#l = list(filter(lambda x: x.endswith('.mp3'), os.listdir(DESKTOP)))
#for fn in l:
go = True
for p in [plv.NEWESTPATH] + plv.MOVESTUFFDIRS:
    if not os.path.exists(p):
        print 'Not found: '+p
        go = False
doCopy = True
if '-nc' in sys.argv:
    print 'movestuff.py: Not copying.'
    doCopy = False
if go:
    redir = ' '+plv.redirect_stderr
    for extn in plv.extns:
        for msd in plv.MOVESTUFFDIRS:  
            if doCopy:
                os.system('cp "'+msd+'/"*.'+extn+' "'+plv.NEWESTPATH+'"'+redir)
            os.system('mv "'+msd+'/"*.'+extn+' "'+plv.LOCALSONGSPATH+'"'+redir)
