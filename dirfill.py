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
    global ctr, files
    for f in sorted(listdir(d)): #azutils listdir function that works with unicode strings
        f = os.path.join(d, f)
        if not os.path.isdir(f):
            x = f.rpartition('.')[2].lower()
            if x in plv.extns and f not in filesAlreadyInList:
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
                recurlist(f, basicInfo)

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
    print '\n'+str(ctr)+' new entries found.\nSaving '+os.path.basename(path)+'...'
    out = open(path, type)
    out.writelines(files)
    out.close()

def main():
    global ctr, files, filesAlreadyInList, dirs, dirCtr
    init()
    if '-a' in sys.argv:
        findAllDirsIn(plv.ROOTDIR)
        print '\n'+str(dirCtr)+' directories found.\nSaving albums.txt...'
        fwrite(dirs, plv.albumfile)
    if '-n' in sys.argv:
        l = dirFillToList()
        filesAlreadyInList = list(map(lambda x: x[0], l))
        recurlist(plv.NEWESTPATH)
        writeSongLines(plv.DIRFILLPATH, 'ab')
    else:
        recurlist(plv.ROOTDIR)
        writeSongLines(plv.DIRFILLPATH, 'wb')
        init()
        recurlist(plv.LOCALSONGSPATH, basicInfo=True)
        writeSongLines(plv.localDirfillFile, 'wb')
    os.system('python2.7 redo_tags.py '+' '.join(sys.argv[1:]))
    waitAtEnd()

if __name__ == '__main__':
    main()

