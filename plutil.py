#!/usr/bin/env python

# for functions used by other parts, like dirfill.py, in addition to playlistmaker.py
# if used only in playlistmaker.py, put it there.
# if it has even wider use, put it in azutils

import datetime, time, calendar, os, subprocess, shutil, sys, unicodedata
import plvars as plv
from azutils import *

class ParseCmdResult:
    def __init__(self):
        self.careAboutNegs = False
        self.terms = []
        self.negTerms = []
        #self.flags = []
        self.params = {}

class Tag(object):
    tagsByAlias = {}
    tagsByName = {}
    def __init__(self, name = '', songs = None, aliases = None):
        if songs == None:
            songs = []
        if aliases == None:
            aliases = []
        self.data = {'name' : name,
                     'songs' : songs,
                     'aliases' : aliases}
        self.hasPriority = False
        self.priority = 0
    def addAlias(self, s):
        if s in Tag.tagsByAlias:
            print 'Alias "'+s+'" already in use.'
            return False
        else:
            Tag.tagsByAlias[s] = self
            self.data['aliases'].append(s)
            return True
    def delAlias(self, s):
        if Tag.tagsByAlias[s] != self:
            print 'Alias "'+s+'" is not for this tag.'
            return False
        else:
            del Tag.tagsByAlias[s]
            self.data['aliases'].remove(s)
            return True
    def __cmp__(self, other):
        if not (self.hasPriority == other.hasPriority):
            if (self.hasPriority):
                return -1
            else:
                return 1
        elif (self.priority != other.priority):
            return self.priority - other.priority
        else:
            return cmp(self.data['name'], other.data['name'])
    def __eq__(self, other):
        if type(other) == Tag:
            return cmp(self, other) == 0
        return False
    def __ne__(self, other):
        return not (self == other)
        
def getTag(name):
    return next((tag for tag in plv.tags if tag.data['name'] == name), None)
    #return filter(lambda x: x.data['name'] == name, plv.tags)[0]
    
def tagsToNames(l):
    return map(lambda x: x.data['name'], l)

class DirData(object):
    def __init__(self, fn):
        self.data = {'fn' : fn }

class SongData(object):
    def __init__(self, fn, sk = '', rating = 0, tags = None, mtime = plv.cZeroTime):
        if tags == None:
            tags = []
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
    def getArtistAndTitle(self):
        if '-' in self.data['sk']:
            artist,temp,title = self.data['sk'].partition('-')
            return artist.strip(),title.strip()
        return ('','')
    def hasNoNonTrivialTags(self):
        for t in self.data['tags']:
            if t.data['name'] not in plv.TRIVIAL_TAGS:
                return False
        return True
            
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
        #k = os.path.basename(fn).lower()
        k = unorm(fn.rpartition(plv.cSep)[2].lower())
        if k in ret:
            ret[k].append(fn)
        else:
            ret[k] = [fn]
    return ret

def bracketNum(n):
    return '[%3d] '%n

def fileIsNew(fn, n):
    return datetime.date.today() - datetime.date.fromtimestamp(os.stat(fn).st_mtime) < datetime.timedelta(days=n)

def readSplitList(fn):
    ret = map(lambda x: x.split('\t'), clean(fread(fn)))
    return ret

def dirFillToList():
    infile = tryOpen(plv.DIRFILLPATH, 'rb')
    dfl = map(lambda x: x.decode('utf').strip().split('\t'), infile.readlines())
    for item in dfl:
        item[0] = unorm(item[0])
        item[1] = unorm(item[1])
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
    if not os.path.exists(plv.ROOTDIR):
        print plv.cIpodMissing
    fwrite(songNames, fn)
    return localCtr[0]

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
    
def playPlaylist(fn, itunesFlag):
    print 'Playing: '+fn
    if itunesFlag:
        mp = plv.second_mediaplayer
    else:
        mp = plv.mediaplayer
    subprocess.Popen(mp.split(' ')+[fn])    
    
def playSongs(inputSongs, optdict):
    sort = optdict['sort']
    itunesFlag = optdict['itunesFlag']
    try:
        if plv.NOIPODMODE:
            print 'Only playing local songs.'
            songs = [song for song in inputSongs if song.data['locals'] != []]
        else:
            songs = inputSongs
        localCtr = writePls(plv.LASTPLSPATH, songs, sort, localFlag=True)
        print str(localCtr)+' local files used. (%.0f%%)' % ((localCtr*100)/float(len(songs)))
        if not ('addFlag' in optdict and optdict['addFlag']):
            killVLC()
        else:
            print 'Not killing VLC.'
        if itunesFlag:
            mp = plv.second_mediaplayer
        else:
            mp = plv.mediaplayer
            if plv.USE_VLC_RC:
                os.system(mp+' '+plv.LASTPLSPATH+' > /dev/null &')
                time.sleep(plv.VLCSOCK_DELAY) #kludge to make sure vlc is up and running before sending play signal
                addMacro('/msg play')
            else:
                subprocess.Popen(mp.split(' ')+[plv.LASTPLSPATH])
#        subprocess.Popen(mp.split(' ')+[plv.LASTPLSPATH])
#        print mp.split(' ')+[plv.LASTPLSPATH]
#        os.system(mp+' '+plv.LASTPLSPATH+' &')
        return True
    except:
        return False

def playSong(fn, optdict):
    return playSongs([fn], optdict)

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

def tagListToString(taglist):
    return ', '.join(map(lambda x: x.data['name'], taglist))

def ratingString(r):
    return "%g" % r

def ratingToString(r):
    if r == 0:
        return ''
    else:
        return ratingString(r)
    
def callDirfill():
#    subprocess.Popen(['python', 'dirfill.py'])
    os.system('~/pystuff/playlistmaker/dirfill.py -a -nr')
    
def doesGenreFolderExist(s):
    p = opj(plv.GENRESPLITPATH, s)
    return os.path.exists(p)

#LOCKING MECHANISM

def isLocked():
    return os.path.exists(plv.lock_file)

def lock():
    #print 'Creating "'+plv.lock_file+'"'
    #os.system('type nul > "'+plv.lock_file+'"')
    os.system('touch "'+plv.lock_file+'"')
    
def unlock():
    if isLocked():
        os.system('rm '+plv.lock_file)
    
def checkLock():
    if not isLocked():
        lock()
        return True
    else:
        s = raw_input('Lock file exists. Kill? (y/N) ')
        if (s.lower() == 'y'):
            print 'Unlocking.'
            unlock()
            return True 
        else:
            print 'Not unlocking. Bye!'
            return False
        
def unorm(s):
    return unicodedata.normalize(plv.cEncoding, s)
    
def killVLC():
    os.system("kill `ps aux | grep /Applications/VLC.app/Contents/MacOS/VLC | awk '{print $2}'` "+plv.redirect_stderr)
    
def genericSearchStringMacro(searchTerm, commandStr, args):
    argsAsStr = '"' + '" "'.join(args) + '"'
    s = '.'+searchTerm+';/'+commandStr+' '+argsAsStr+';/goto '+str(plv.rptr)
    return s