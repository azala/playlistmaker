# for functions used by other parts, like dirfill.py, in addition to playlistmaker.py
# if used only in playlistmaker.py, put it there.
# if it has even wider use, put it in azutils

import datetime, time, calendar, os, subprocess, shutil
import plvars as plv
from azutils import *

def mainBackupDir():
    return plv.BACKUPDIRS[0]

def findFirstAlpha(s):
    for i in range(0, len(s)):
        if s[i].isalpha():
            return i
    return -1

def pathToFileNameKey(p):
    x = p.rpartition('\\')[2].lower()
    a = findFirstAlpha(x)
    if a != -1:
        x = x[a:]
    return x

def bracketNum(n):
    return '[%3d] '%n

def fileIsNew(fn, n):
    return datetime.date.today() - datetime.date.fromtimestamp(os.stat(fn).st_mtime) < datetime.timedelta(days=n)

def dirFillToList():
    infile = tryOpen(plv.DIRFILLPATH, 'rb')
    dfl = map(lambda x: x.decode('utf').strip().split('\t'), infile.readlines())
    infile.close()
    return dfl

def dataToDirFillLine(l):
    return ('\t'.join(l)+'\r\n').encode('utf')

def writePls(fn, songlist, sort):
    if sort:
        sl = sorted(songlist, key=lambda x: plv.fileNames2sortKeys[x])
    else:
        print 'Not sorting this playlist.'
        sl = sorted(songlist)
    sl = unclean(sl)
    fwrite(sl, fn)
    
def replaceDirFillEntry(mfqEntries):
    if mfqEntries == []:
        return
    f = open(plv.DIRFILLPATH, 'rb')
    dfLines = f.readlines()
    f.close()
    g = open(plv.DIRFILLPATH, 'wb')
    for l in dfLines:
        repStr = None
        for e in mfqEntries:
            if l.decode('utf-8').startswith(e[0]+'\t'):
                repStr = e[2]+'\t'+e[3]+'\t'+dateTimeStr(plv.fileNames2Dates[e[2]])+'\r\n'
                break
        if repStr == None:
            g.write(l)
        else:
            g.write(repStr.encode('utf'))
    g.close()
    print 'Applied moved files to dirfill.txt.'

def tryPrint(s, prefix = ''):
    try:
        print prefix + s
    except:
        print prefix + '(can\'t print)'

def backupDirFilter(x, bkdir):
    if not os.path.isdir(opj(bkdir, x)):
        return False
    return x.count('-') == 3
        
def needAutoBackup(bdir = mainBackupDir()):
    d = os.listdir(bdir)
    d = filter(lambda x: backupDirFilter(x, bdir), d)
    if d == []:
        return True
    #d = list(map(lambda x: os.stat(opj(bdir, x)).st_mtime, d))
    d = map(invDateTimeStr, d)
    latest = max(d)
    a = invTimetuple(latest)
    b = invTimetuple(time.gmtime())
    if False: #I might want this later
        print b-a, 'since last backup.'
    return b - a >= datetime.timedelta(days=plv.AUTOBACKUP_INTERVAL)
    
def playFiles(files, sort = True):
    try:
        writePls(plv.LASTPLSPATH, files, sort)
        subprocess.Popen([plv.mediaplayer, plv.LASTPLSPATH])
        return True
    except:
        return False

def playFile(fn, sort = True):
    return playFiles([fn], sort)

def addMacro(s):
    plv.cmdQueue = doubleSlash(s).split(';') + plv.cmdQueue

def waitAtEnd():
    if plv.WAITATEND:
        print '(Press ENTER to exit.)'
        input()

def saveLog():
    f = tryOpen(plv.cmdLogFile, 'ab')
    loglines = map(lambda x: (x+'\r\n').encode('utf'), plv.cmdLog)
    f.writelines(loglines)
    plv.cmdLog = []
    f.close()
    
def fileAge(key):
    # returns a timedelta
    return invTimetuple(time.gmtime()) - invTimetuple(plv.fileNames2Dates[key])

def copy(src, dst):
    shutil.copy(src, dst)
