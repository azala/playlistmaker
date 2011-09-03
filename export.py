#!/usr/bin/env python

import plvars as plv, sys, os, subprocess

subprocess.call([os.path.join(plv.PLMAKERDIR, 'inexhelper.py'), '-ex']+sys.argv[1:])