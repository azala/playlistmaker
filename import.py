#!/usr/bin/env python

import plvars as plv, sys, os, subprocess

subprocess.call([os.path.join(plv.PLMAKERDIR, 'inexhelper.py'), '-in']+sys.argv[1:])