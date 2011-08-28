#!/usr/bin/env python

from azutils import *
import plvars as plv

class Command(object):
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
    def asStr(self):
        return '  '+self.name+': '+self.desc

def makeCmd(c):
    if ': ' in c:
        params = c.split(': ')
    else:
        params = [c, '']
    #print('Imported command: '+params[0])
    return Command(params[0], params[1])

def findCmd(name):
    for c in plv.commandlist:
        if c.name == name:
            return c
    return None

cl = clean(fread(plv.cmdListFile))
plv.commandlist = map(makeCmd, cl)
