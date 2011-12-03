#!/usr/bin/env python

import plvars as plv, os

os.system('./rename.py "'+plv.REALLYNEWESTPATH+'" 1100')
for msd in plv.MOVESTUFFDIRS:
    os.system('./rename.py "'+msd+'" 1000')