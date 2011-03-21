# for functions used by other parts, like dirfill.py, in addition to playlistmaker.py
# if used only in playlistmaker.py, put it there.
# if it has even wider use, put it in azutils

import datetime, time, calendar, os, subprocess, shutil, sys
import plvars as plv
from azutils import *

class Tag(object):
    def __init__(self, name = '', songs = []):
        self.data = {'name' : name,
                     'songs' : songs}
        
def getTag(name):
    return next((tag for tag in plv.tags if tag.data['name'] == name), None)
    #return filter(lambda x: x.data['name'] == name, plv.tags)[0]

class DirData(object):
    def __init__(self, fn):
        self.data = {'fn' : fn }

class SongData(object):
    def __init__(self, fn, sk = '', rating = 0, tags = [], mtime = plv.cZeroTime):
        self.data = {'fn' : fn,
                     'sk' : sk,
                     'rating' : rating,
                     'tags' : tags,
                     'mtime' : mtime,
                     'locals' : []}
        self.updateName(fn)
        if sk != '':
            self.updateKey(sk)
    def updateNameOrKey(self, news, s):
        olds = self.data[s]
        if olds in plv.songDict[s]:
            if olds != news:
                plv.songDict[s][news] = plv.songDict[s][olds]
                del plv.songDict[s][olds]
                self.data[s] = news
        else:
            plv.songDict[s][news] = self
            self.data[s] = news
    def updateName(self, fn):
        self.updateNameOrKey(fn, 'fn')
    def updateKey(self, sk):
        self.updateNameOrKey(sk, 'sk')
            
def getSongs(attrName, attrValue, songs):
    return filter(lambda x: x.data[attrName] == attrValue, songs)

def getSong(name):
    #x = getSongs('fn', name, plv.songs)
    #for s in x:
    #    if 'VACANCY' in s.data['fn']:
    #        print s.data
    return next((song for song in plv.songs if song.data['fn'] == name), None)
    #return getSongs('fn', name, plv.songs)[0] #because it better return only one result...

def mainBackupDir():
    return plv.BACKUPDIRS[0]

def findFirstAlpha(s):
    for i in range(0, len(s)):
        if s[i].isalpha():
            return i
    return -1

def pathToFileNameKey(p):
    x = os.path.basename(p).lower()
    a = findFirstAlpha(x)
    if a != -1:
        x = x[a:]
    return x

#takes a list of filenames
def shortNameToFullDict(l):
    ret = {}
    for fn in l:
        k = os.path.basename(fn).lower()
        if k in ret:
            ret[k].append(fn)
        else:
            ret[k] = [fn]
    return ret

def bracketNum(n):
    return '[%3d] '%n

def fileIsNew(fn, n):
    return datetime.date.today() - datetime.date.fromtimestamp(os.stat(fn).st_mtime) < datetime.timedelta(days=n)

def readSongList(fn):
    dfl = map(lambda x: x.split('\t'), clean(fread(fn)))
    return dfl

def dirFillToList():
    infile = tryOpen(plv.DIRFILLPATH, 'rb')
    dfl = map(lambda x: x.decode('utf').strip().split('\t'), infile.readlines())
    infile.close()
    return dfl

def dataToDirFillLine(l):
    return ('\t'.join(l)+'\r\n').encode('utf-8')

def mapSongsToNames(l):
    return map(lambda x: x.data['fn'], l)

def getLocalCopy(song, ctr):
    x = song.data['locals']
    if x == []:
        return song.data['fn']
    else:
        ctr[0] += 1
        return x[0]

def writePls(fn, songlist, sort, localFlag=False):
    if sort:
        songlist = sorted(songlist, key=lambda x: x.data['sk'])
    else:
        print 'Not sorting this playlist.'
    localCtr = [0]
    if localFlag:
        func = lambda x: getLocalCopy(x, localCtr)
    else:
        func = lambda x: x.data['fn']
    songNames = unclean(map(func, songlist))
    fwrite(songNames, fn)
    return localCtr[0]
    
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
    d = listdir(bdir)
    d = filter(lambda x: backupDirFilter(x, bdir), d)
    if d == []:
        return True
    #d = list(map(lambda x: os.stat(opj(bdir, x)).st_mtime, d))
    d = map(invDateTimeStr, d)
    latest = max(d)
    a = invTimetuple(latest)
    b = invTimetuple(time.gmtime())
    #print b-a, 'since last backup.' (I might want this later)
    return b - a >= datetime.timedelta(days=plv.AUTOBACKUP_INTERVAL)
    
def playPlaylist(fn):
    print 'Playing: '+fn
    subprocess.Popen([plv.mediaplayer, fn])    
    
def playSongs(songs, sort = True):
    try:
        localCtr = writePls(plv.LASTPLSPATH, songs, sort, localFlag=True)
        print str(localCtr)+' local files used. (%.0f%%)' % ((localCtr*100)/float(len(songs)))
        subprocess.Popen([plv.mediaplayer, plv.LASTPLSPATH])
        return True
    except:
        return False

def playSong(fn, sort = True):
    return playSongs([fn], sort)

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
    
def tagsAsString(fn):
    if fn in plv.taglists:
        tl = plv.taglists[fn]
    else:
        tl = []
    return tagListToString(tl)

def tagListToString(taglist):
    return ', '.join(taglist)

def ratingToString(r):
    if r == 0:
        return ''
    else:
        return str(r)


    