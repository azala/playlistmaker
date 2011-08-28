#!/usr/bin/env python

import os
import plvars as plv

#l = list(filter(lambda x: x.endswith('.mp3'), os.listdir(DESKTOP)))
#for fn in l:
go = True
for p in [plv.NEWESTPATH, plv.REALLYNEWESTPATH, plv.DESKTOP]:
    if not os.path.exists(p):
        print 'Not found: '+p
        go = False
if go:
    os.system('cp "'+plv.DESKTOP+'*.mp3" "'+plv.NEWESTPATH+'"')
    os.system('mv "'+plv.DESKTOP+'*.mp3" "'+plv.LOCALSONGPATH+'"')
    #reallynewest
    os.system('copy "'+plv.REALLYNEWESTPATH+'*.mp3" "'+plv.LOCALSONGPATH+'" /y')
    os.system('move "'+plv.REALLYNEWESTPATH+'*.mp3" "'+plv.NEWESTPATH+'"')
