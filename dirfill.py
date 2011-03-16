import sys, os, os.path, subprocess
import plvars as plv
from plutil import *

if not os.path.exists(plv.ROOTDIR):
    print 'Not found: '+plv.ROOTDIR
    sys.exit(0)

ctr = 0
files = []
filesAlreadyInList = []

def recurlist(d):
    global ctr, files
    for f in sorted(listdir(d)): #azutils listdir function that works with unicode strings
        f = os.path.join(d, f)
        if not os.path.isdir(f):
            x = f.rpartition('.')[2].lower()
            if x in plv.extns and f not in filesAlreadyInList:
                files.append(dataToDirFillLine([f,
                                                pathToFileNameKey(f),
                                                dateTimeStr(time.gmtime(os.path.getctime(f))),
                                                ]))
                ctr += 1
                if ctr % 500 == 0:
                    print ctr
        else:
            if f not in plv.excludedirs:
                recurlist(f)

dirs = []
dirCtr = 0
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

if '-a' in sys.argv:
    findAllDirsIn(plv.ROOTDIR)
    print '\n'+str(dirCtr)+' directories found.\nSaving albums.txt...'
    fwrite(dirs, plv.albumfile)
if '-n' in sys.argv:
    l = dirFillToList()
    filesAlreadyInList = list(map(lambda x: x[0], l))
    recurlist(plv.NEWESTPATH)
    print '\n'+str(ctr)+' new entries found.\nSaving dirfill.txt...'
    out = open(plv.DIRFILLPATH, 'ab')
    out.writelines(files)
    out.close()
else:
    d = plv.ROOTDIR
    recurlist(d)
    print '\n'+str(ctr)+' entries found.\nSaving dirfill.txt...'
    out = open(plv.DIRFILLPATH, 'wb')
    out.writelines(files)
    out.close()

#subprocess.call(['python2.7', 'redo_tags.py']+sys.argv[1:])
os.system('python2.7 redo_tags.py '+' '.join(sys.argv[1:]))

waitAtEnd()

