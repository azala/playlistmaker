#!/usr/bin/env python

import plvars as plv, os

for msd in plv.MOVESTUFFDIRS:
    os.system('./rename.py "'+msd+'" 1000')