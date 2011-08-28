#!/usr/bin/env python

import sys, os, os.path, subprocess
import plvars as plv
from plutil import *

if not os.path.exists(plv.ROOTDIR):
    print 'Not found: '+plv.ROOTDIR
    sys.exit(0)

def init():
    global ctr, files, filesAlreadyInList, dirs, dirCtr
    ctr = 0
    files = []
    filesAlreadyInList = []
    dirs = []
    dirCtr = 0

def recurlist(d, basicInfo=False):
    global files
    files = []
    print 'Browsing: '+d
    recurlistHelper(d, basicInfo)

def recurlistHelper(d, basicInfo):
    global ctr, files
    for f in sorted(listdir(d)): #azutils listdir function that works with unicode strings
        f = os.path.join(d, f)
        if not os.path.isdir(f):
            x = f.rpartition('.')[2].lower()
            if x in plv.extns and f not in filesAlreadyInList:
                #exclude mac's stupid ._ files
                if f.rpartition('\\')[2].startswith('._'):
                    print 'Found mac fake file: '+f
                else:
                    if basicInfo:
                        datalist = [f]
                    else:
                        datalist = [f,
                                    pathToFileNameKey(f),
                                    dateTimeStr(time.gmtime(os.path.getctime(f))),
                                    ]
                    files.append(dataToDirFillLine(datalist))
                    ctr += 1
                    if ctr % 500 == 0:
                        print ctr
        else:
            if f not in plv.excludedirs:
                recurlistHelper(f, basicInfo)

def findAllDirsIn(d):
    global dirs, dirCtr
    for f in sorted(listdir(d)):
        f = opj(d, f)
        if os.path.isdir(f) and f not in plv.excludedirs:
            dirCtr += 1
            dirs.append((f+'\r\n').encode('utf'))
            if dirCtr % 20 == 0:
                print dirCtr
            findAllDirsIn(f)
            
def writeSongLines(path, type):
    global ctr, files
    print str(ctr)+' new entries found.\nSaving '+os.path.basename(path)+'...\n'
    out = open(path, type)
    out.writelines(files)
    out.close()

def main():
    global ctr, files, filesAlreadyInList, dirs, dirCtr
    init()
    if '-a' in sys.argv:
        d = plv.ROOTDIR
        print 'Browsing albums: '+d
        findAllDirsIn(d)
        print str(dirCtr)+' directories found.\nSaving albums.txt...\n'
        fwrite(dirs, plv.albumfile)
    if '-n' in sys.argv:
        l = readSplitList(plv.DIRFILLPATH)
        filesAlreadyInList = list(map(lambda x: x[0], l))
        recurlist(plv.NEWESTPATH)
        mode = 'ab'
        writeSongLines(plv.DIRFILLPATH, mode)
        l = readSplitList(plv.localDirfillFile)
        filesAlreadyInList = list(map(lambda x: x[0], l))
    else:
        recurlist(plv.ROOTDIR)
        mode = 'wb'
        writeSongLines(plv.DIRFILLPATH, mode)
        init()
    recurlist(plv.LOCALSONGSPATH, basicInfo=True)
    writeSongLines(plv.localDirfillFile, mode)
    os.system('python2.7 redo_tags.py '+' '.join(sys.argv[1:]))
    waitAtEnd()

if __name__ == '__main__':
    main()

