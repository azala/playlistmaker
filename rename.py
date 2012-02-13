#!/usr/bin/env python

import os, sys, re, azutils
import plvars as plv

RENAME = False
RECURSIVE = False
LISTALL = False
LIMIT_MATCHES = False
CHAR_REPLACE_DIR = { '\uff5e' : '~' }
ANNIHILATE_THRESHOLD = 1000000 #1 megabyte

def altRename(old, new):
    global RENAME
    if RENAME:
        try:
            os.rename(old, new)
            print 'Successful rename: '+new
        except:
            print 'Failed rename: '+new
        
def standard_rename_op(s):
    global CHAR_REPLACE_DIR
    split = os.path.split(s)
    fn = split[1]
    for c in CHAR_REPLACE_DIR:
        fn = fn.replace(c, CHAR_REPLACE_DIR[c])
    fn = fn.replace("www.mrtzcmp3.net","")
    fn = fn.replace("_"," ")
    fn = fn.replace("amp;","&")
    fn = re.sub(r"\ {2,}"," ",fn)
    fn = re.sub("(\([0-9]*\))?.mp3",".mp3",fn)
    fn = re.sub(" ?-.mp3",".mp3",fn)
    if "-" in fn:
        l = list(fn.partition("-"))
        if len(l[0]) < 2 and "-" in l[2]:
            ll = l[2].partition("-")
            l[0] += "-"+ll[0]
            l[2] = ll[2]
        fn = l[0].strip()+" - "+l[2][:-4].strip()+".mp3"
    ret = os.path.join(split[0], fn)
    return ret
        
def convert(s):
    if not s.endswith(".mp3"):
        return False
    if annihilateDotUnderscore(s):
        return False
    split = os.path.split(s)
    fn = split[1]
    for c in CHAR_REPLACE_DIR:
        fn = fn.replace(c, CHAR_REPLACE_DIR[c])
    fn = fn.replace("www.mrtzcmp3.net","")
    fn = fn.replace("_"," ")
    fn = fn.replace("amp;","&")
    fn = re.sub(r"\ {2,}"," ",fn)
    fn = re.sub("(\([0-9]*\))?.mp3",".mp3",fn)
    fn = re.sub(" ?-.mp3",".mp3",fn)
    if "-" in fn:
        l = list(fn.partition("-"))
        if len(l[0]) < 2 and "-" in l[2]:
            ll = l[2].partition("-")
            l[0] += "-"+ll[0]
            l[2] = ll[2]
        fn = l[0].strip()+" - "+l[2][:-4].strip()+".mp3"
    ret = os.path.join(split[0], fn)
    if s != ret:
        altRename(s, ret)
        return True
    else:
        print 'No rename needed: '+s
    return False

def renameFiles(d, maxmatches, ctr):
    global RECURSIVE, LISTALL
    basedir = d
    subdirlist = []
    try:
        listd = os.listdir(d)
    except:
        print 'Couldn\'t open: '+d
        return 0
    for item in listd:
        try:
            fullitem = os.path.join(basedir, item)
            if not os.path.isdir(fullitem):
                if maxmatches == -1 or ctr < maxmatches:
                    if convert(fullitem):
                        ctr += 1
                else:
                    return ctr
            else:
                if RECURSIVE:
                    subdirlist.append(fullitem)
            if LISTALL:
                try:
                    pass
                    #print item
                except:
                    pass
        except UnicodeEncodeError as e:
            print "Unicode Error: Cannot interpret file name."
            pass
    for subdir in subdirlist:
        ctr = renameFiles(subdir, maxmatches, ctr)
    return ctr

def annihilateDotUnderscore(s):
    global ANNIHILATE_THRESHOLD
    t = s.rpartition(azutils.cSep)[2]
    if (len(t) >= 2 and t[0] == '.' and os.path.exists(s) and os.stat(s).st_size < ANNIHILATE_THRESHOLD):
        os.system('rm "'+s+'"')
        print 'Dot-trashed "'+s+'".'
        return True
    return False

def main():
    global RENAME, RECURSIVE, LISTALL, LIMIT_MATCHES

    if len(sys.argv) < 2:
        print "Usage: ./rename.py <dirname> <options>"
        return
    if len(sys.argv) == 2:
        opts = "0010"
    else:
        opts = sys.argv[2]

    maxmatches = -1
    if opts[0] == "1":
        RENAME = True
    if opts[1] == "1":
        RECURSIVE = True
    if opts[2] == "1":
        LISTALL = True
    if opts[3] == "1":
        LIMIT_MATCHES = True
        maxmatches = 10
        
    renameFiles(sys.argv[1], maxmatches, 0)
    return

if __name__ == "__main__":
    main()


