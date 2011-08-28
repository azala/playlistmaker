#!/usr/bin/env python

f = open('plvars.py', 'rb')
varlist = []
for l in f.readlines():
    x = l.decode('utf')
    if ' = ' in x:
        varlist.append(x.split(' = ')[0])
f.close()
g = open('playlistmaker.py', 'rb')
h = open('new_pl.py', 'wb')
gg = map(lambda x: x.decode('utf'), g.readlines())
for l in gg:
    for v in varlist:
        l = l.replace(v, 'plv.'+v)
    h.write(l.encode('utf'))
g.close()
h.close()
