#!/usr/bin/env python

import os, sys
import plvars as plv

#l = list(filter(lambda x: x.endswith('.mp3'), os.listdir(DESKTOP)))
#for fn in l:
go = True
for p in [plv.NEWESTPATH, plv.REALLYNEWESTPATH, plv.DESKTOP]:
    if not os.path.exists(p):
        print 'Not found: '+p
        go = False
doCopy = True
if '-nc' in sys.argv:
    print 'movestuff.py: Not copying.'
    doCopy = False
if go:
    redir = ' '+plv.redirect_stderr
    if doCopy:
        os.system('cp "'+plv.DESKTOP+'/"*.mp3 "'+plv.NEWESTPATH+'"'+redir)
    os.system('mv "'+plv.DESKTOP+'/"*.mp3 "'+plv.LOCALSONGSPATH+'"'+redir)
    os.system('cp "'+plv.REALLYNEWESTPATH+'/"*.mp3 "'+plv.LOCALSONGSPATH+'"'+redir)
    os.system('mv "'+plv.REALLYNEWESTPATH+'/"*.mp3 "'+plv.NEWESTPATH+'"'+redir)
