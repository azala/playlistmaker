#!/usr/bin/env python

import os, datetime, shutil, time, subprocess, plutil, operator, readline
from command import *
import plvars as plv
from plutil import *
from shell import *

def nothingToDo():
    return not plv.invalidateAllTags and \
        plv.invalidateTheseTags == [] and \
        plv.needRewriteDirfill == False and \
        plv.ratingdataChanged == False and \
        plv.aliasesChanged == False

def removeAllTagsForFile(fn):
    song = plv.songDict['fn'][fn]
    for tag in song.data['tags']:
        removeTagFromSong(tag, song)

def invalidate(t = None):
    if t == None:
        if plv.invalidateAllTags:
            return
        plv.invalidateAllTags = True
        plv.invalidateTheseTags = []
        print 'Invalidated all tags.'
    elif t not in plv.invalidateTheseTags and not plv.invalidateAllTags:
        print 'Invalidated tag: '+t.data['name']
        plv.invalidateTheseTags.append(t)

def revalidate():
    plv.invalidateTheseTags = []
    plv.invalidateAllTags = False

def readRatingData():
    for l in clean(fread(plv.ratingFile)):
        k, v = l.split('\t')
        k = unorm(k)
        plv.songDict['fn'][k].data['rating'] = float(v)
        plv.ratingdata[k] = float(v)
    print 'Loaded rating data.'
    
#---FILE MOVE
# I hate this code. Come up with a better data model...
def moveFile(src, dst, banish = False):
    # src and dst are strings
    if src == dst:
        print 'Failed, both names are the same.'
        return
#    try:
#        subprocess.check_call(['move', src, dst], shell=True)
#    except (subprocess.CalledProcessError, WindowsError) as e:
#        print 'Move failed: '+str(e)
#        return
    try:
        subprocess.check_call(['mv',src,dst], shell=True)
    except:
        print 'Move failed: '+str(e)
        return
    song = plv.songDict['fn'][src]
    song.data['fn'] = dst
    song.data['sk'] = dstKey = pathToFileNameKey(dst)
    plv.songDict['fn'][dst] = song
    plv.songDict['sk'][dstKey] = song
    for tag in plv.tags:
        tag.data['songs'] = filter(lambda x: x != song, tag.data['songs'])
        invalidate(tag)
    if banish:
        plv.lines.remove(song)
    print 'Moved "'+os.path.basename(src)+'" to "'+os.path.basename(dst)+'".'
    plv.needToCallDirfill = True
    
def banishFile(fn):
    moveFile(fn, plv.DONTWANTPATH, True)
    
#---SEARCH RESULTS



def newSearch(newResults, causedByThisSearch=''):
    plv.resultHistory = plv.resultHistory[-1*plv.maxStoredResults+1:] + [newResults]
    plv.resultHistoryTerms = plv.resultHistoryTerms[-1*plv.maxStoredResults+1:] + [causedByThisSearch]
    plv.resultHistory_DSFlag = plv.resultHistory_DSFlag[-1*plv.maxStoredResults+1:] + [plv.directorySearch]
    #plv.resultHistory_NoSortFlag = plv.resultHistory_NoSortFlag[-1*plv.maxStoredResults+1:] + [plv.nosort]
    plv.rptr = len(plv.resultHistory)-1
    
def traverse(n):
    if plv.rptr+n >= 0 and plv.rptr+n < len(plv.resultHistory):
        plv.rptr += n
        return True
    return False

def traverseCmd(s, parity):
    if parity == 1:
        ba_string = 'ahead'
    else:
        ba_string = 'back'
    try:
        if s == '':
            s = 1
        else:
            s = int(s)
        if traverse(parity*s):
            print 'Moved '+ba_string+' '+str(s)+' searches.'
            plv.directorySearch = plv.resultHistory_DSFlag[plv.rptr]
            #plv.nosort = plv.resultHistory_NoSortFlag[rptr]
            printResults(mapSongsToNames(readRes()))
        else:
            print 'Couldn\'t move '+ba_string+' '+str(s)+' searches.'
    except:
        print 'Bad argument.'

def readRes():
    if plv.rptr == -1:
        return []
    else:
        return plv.resultHistory[plv.rptr]

def showSearchList():
    for i in range(0, len(plv.resultHistory)):
        if i == plv.rptr:
            pref = "> "
        else:
            pref = "  "
        if (plv.resultHistory_DSFlag[i]):
            albumString = " [ALBUM]"
        else:
            albumString = ""
        print pref + str(len(plv.resultHistory[i])) + " " + plv.resultHistoryTerms[i] + albumString
        
def getAlias(tname, boo = True):
    if tname in Tag.tagsByAlias:
        if boo:
            print 'Using alias "'+Tag.tagsByAlias[tname].data['name']+'".'
        return Tag.tagsByAlias[tname].data['name']
    else:
        return tname
        
def defaultListFilter(l):
    return filter(lambda x: x != '', map(lambda x: x.strip().decode('utf'), l))
        
def fillTagAliases():
    inf = open(plv.tag_aliasfile, 'rb')
    aliasLines = defaultListFilter(inf.readlines())
    inf.close()
    aliasLines = map(lambda x: x.split('\t'), aliasLines)
    for line in aliasLines:
        for k in line[1:]:
            Tag.tagsByName[line[0]].addAlias(k)
        
def getPriorityTagNames():
    ptags = filter(lambda x: x != '', clean(fread(plv.tag_priorityfile)))
    tagsAndPlaylists = readToSplitList(plv.tag_indexfile)
    plv.tagToPlaylist = {x[0]:x[1] for x in tagsAndPlaylists}
    if '' in plv.tagToPlaylist:
        del plv.tagToPlaylist['']
    tags = filter(lambda x: x != '' and x not in ptags, plv.tagToPlaylist.keys())
    tags.sort()
    return ptags, tags

def sortedTags():
    head = plv.ptag_index
    tail = sorted(filter(lambda x: x not in plv.ptag_index, plv.tags))
    return filter(lambda x: x in plv.tags, head + tail)

def doBackup(buf = ['']):
    try:
        params = parseCmd(buf)
    except:
        print 'Invalid input.'
    doE = '-doe' in params
    filelist = filter(lambda x: x.endswith('.txt'), listdir(plv.CDATAPATH))
    curTime = dateTimeStr(time.gmtime())
    fdir = opj(mainBackupDir(), curTime)
    print 'Creating backup in: '+fdir
    os.mkdir(fdir)
    for fn in filelist:
        shutil.copy(opj(plv.CDATAPATH, fn), opj(fdir, fn))
        print 'Backed up: '+fn
    #backup the search log also to a separate dir
    if backup(src=plv.cmdLogFile, bkdirpath=opj(plv.CDATAPATH, 'searchlogs'), oneDir=True):
        tmp = 'created'
    else:
        tmp = 'failed'
    print 'Search log backup '+tmp+'.'
    #
    for otherDir in plv.BACKUPDIRS[1:]:
        if plv.ROOTDIR in otherDir:
            if doE:
                print 'Creating '+plv.ROOTDIR+' backup...'
            else:
                print 'Skipping '+plv.ROOTDIR+' backup.'
                continue
        dstDir = opj(otherDir, curTime)
        shutil.copytree(fdir, dstDir)
        print 'Copied backups to: '+dstDir
    print 'Done.'

def readDirs():
    plv.dirlist = map(DirData, clean(fread(plv.albumfile)))
    
def readtags():
    rawtfLines = readToSplitList(plv.tagfile)
    #rawtfLines = map(lambda x: x.split('\t'), clean(fread(plv.tagfile)))
    tfLines = []
    knownFileNames = []
    invalidateTheseLater = []
    ctr = 0
    for i in range(0, len(rawtfLines)):
        l = rawtfLines[i][:]
        l[0] = unorm(l[0])
        ctr += 1
        tfLines.append(l)
        knownFileNames.append(l[0])
    print 'Imported '+str(ctr)+' tagged files.'
    
    #p-tag code
    plv.ptag_index, tag_index = getPriorityTagNames()
    plv.ptag_index = map(Tag, plv.ptag_index)
    tag_index = map(Tag, tag_index)
    for t in plv.ptag_index + tag_index:
        plv.tags.append(t)
        Tag.tagsByName[t.data['name']] = t
        
    #plv.plkeys = plv.ptag_index + tag_index
    if plv.tags == []:
        print 'Blank tag index file.'
        print 'Generating new playlist order.'
    FIRST = True
    FIRST_TAGGED_SONG_ERROR = True
    for l in tfLines:
        l[0] = unorm(l[0])
        try:
            curSong = plv.songDict['fn'][l[0]]
        except:
            if FIRST_TAGGED_SONG_ERROR:
                print 'Tagged songs not in dirfill:'
                FIRST_TAGGED_SONG_ERROR = False
            print '  '+l[0]
            continue
        for v in l[1:]:
            w = getAlias(v, False)
            if v != w:
                print 'Converting alias "'+v+'" to "'+w+'".'
                invalidate()
            v = w.lower()
            if v not in Tag.tagsByName:
                print '  Indexfile missing tag: '+v
                t = Tag(v)
                plv.tags.append(t)
                Tag.tagsByName[v] = t
                invalidate(t)
            else:
                t = Tag.tagsByName[v]
            #if v not in plv.plkeys:
            #    plv.plkeys.append(v)
            if t in curSong.data['tags']:
                print '  Duplicate tag: '+t.data['name']
                invalidate()
            else:
                curSong.data['tags'].append(t)
            if curSong in t.data['songs']:
                print '  Duplicate song: '+song.data['name']
                invalidate()
            else:
                t.data['songs'].append(curSong)
    for t in invalidateTheseLater:
        invalidate(t)
    print 'Read tags & playlists.'

def readLocalSongs():
    locals = clean(fread(plv.localDirfillFile))
    locals = {os.path.basename(fn).lower():fn for fn in locals}
    #for l in locals:
    #    print l, locals[l]
    for s in plv.songs:
        shortName = os.path.basename(s.data['fn']).lower()
        if shortName in locals:
            s.data['locals'].append(locals[shortName])

def writeHistory():
    readline.write_history_file(plv.historyFile)
    temp = plv.historyFile+'_TEMP'
    os.system('cat '+plv.historyFile+' | egrep -v "/m|//|/wn" > '+temp+'; mv '+temp+' '+plv.historyFile)

#stuff you might search for:
#doWrite, writeout
def writetags():
    if nothingToDo():
        print 'Nothing was done. No need to save.'
        return
    if plv.needToCallDirfill:
        callDirfill()
    #----write tagfile
    tf = open(plv.tagfile, 'wb')
    for song in plv.songs:
        if song.data['tags'] != []:
            line = song.data['fn']+'\t'+'\t'.join(tagsToNames(song.data['tags']))
            tf.write((line+'\r\n').encode('utf'))
    tf.close()
    #----write aliases
    if plv.aliasesChanged:
        outlines = [tag.data['name']+'\t'+'\t'.join(tag.data['aliases']) for tag in filter(lambda x: x.data['aliases'] != [], plv.tags)]
        fwrite(unclean(outlines), plv.tag_aliasfile)
        print 'Wrote aliases.'
        plv.aliasesChanged = False
    #----write rating data
    if plv.ratingdataChanged:
        rdlist = filter(lambda x: x.data['rating'] != 0, plv.lines)
        fwrite(unclean([song.data['fn']+'\t'+str(song.data['rating']) for song in rdlist]), plv.ratingFile)
        print 'Wrote rating data.'
    plv.ratingdataChanged = False
    #----write playlists
    if plv.invalidateAllTags and not plv.NOIPODMODE:
        wipePlaylists()
    ctr = 0
    playlistCtr = 0
    tif = open(plv.tag_indexfile, 'wb')
    if plv.invalidateAllTags:
        countModifiedTags = len(plv.tags)
    else:
        countModifiedTags = len(filter(lambda x: x.data['songs'] != [] and x in plv.invalidateTheseTags, plv.tags))
    ipod_exists = True
    #----check ipod before writing playlists
    if not os.path.exists(plv.ROOTDIR):
        print plv.cIpodMissing
        ipod_exists = False
    for t in sortedTags():
        tname = t.data['name']
        tsongs = t.data['songs']
        if tsongs == []:
            continue
        playlistCtr += 1
        curPlaylistName = '[%02d]'%playlistCtr + tname + plv.plExt
        tif.write((tname+'\t'+curPlaylistName+'\r\n').encode('utf'))
        if not plv.invalidateAllTags and t not in plv.invalidateTheseTags:
            continue
        elif not ipod_exists:
            continue
        else:
            pf = open(opj(plv.ROOTDIR, curPlaylistName), 'wb')
            tsongs.sort(key=lambda x: x.data['sk'])
            ctr += 1
            print 'Writing: ('+str(ctr)+'/'+str(countModifiedTags)+') '+tname
            for song in tsongs:
                fn = song.data['fn']
                pf.write((fn.replace(plv.ROOTDIR, '').replace('\\','/')+'\r\n').encode('utf'))
            pf.close()
    tif.close()
    revalidate()
    print 'Done writing.'
    

def isTheCommand(x, cmdShortString, lbuf = [None]):
    n = len(cmdShortString)
    if x == '/' + cmdShortString:
        lbuf[0] = ''
        return True
    elif len(x) >= n+3 and x[:n+2] == '/' + cmdShortString + ' ':
        lbuf[0] = x[n+2:]
        return True
    else:
        return False

def getCommandFromInput(x):
    xx = x.split(' ')[0]
    if xx[0] == '/':
        return xx[1:]
    else:
        return ''

def doTheCommand(x, cmdShortString, lbuf = [None]):
    b = isTheCommand(x, cmdShortString, lbuf)
    if b:
        s = plv.FUNC_PREFIX+cmdShortString
        if s not in globals():
            print 'Failed command?'
        else:
            globals()[s](lbuf)
    return b

def cmd_automp(buf):
    addMacro('/kill na -i;-"'+plv.ALBUMPATH+';/tag na";/kill mp -i;/over 6;/tag mp;/kill np -i;/over 1;/tag np')

def increment_autotag_index():
    while True:
        plv.cur_autotag_index += 1
        n = plv.cur_autotag_index
        if n >= len(plv.autotag_saved_search):
            return False
        if plv.autotag_saved_search[n].hasNoNonTrivialTags():
            break
    print '[%d] '%(n+1)+plv.autotag_saved_search[n].data['fn']
    print ', '.join(tagsToNames(plv.autotag_saved_search[n].data['tags']))
    return True

def cmd_at(buf):
    optionlist = ['-s']
    pcr, optionlist = parseCmdWithOptions(buf[0], optionlist)
    if plv.directorySearch:
        print 'Can\'t autotag directories.'
    if '-s' not in optionlist: #skip macro
        addMacro('"'+plv.NEWESTPATH+'";/at -s')
    else:
        if len(plv.rr) == 0:
            print 'Can\'t do much with nothing.'
            return
        Shell.openShell('autotag')
        print 'Opening autotag shell.'
        plv.cur_autotag_index = -1
        plv.autotag_saved_search = plv.rr
        increment_autotag_index()
        
def autotag_handler(x):
    pcr = parseCmdHelper(x)
    for t in pcr.terms:
        doTag(t, [plv.autotag_saved_search[plv.cur_autotag_index]])
        print
    if not increment_autotag_index():
        print 'Reached the end, exiting autotag.'
        addMacro('\q')

def cmd_q(buf):
    if Shell.curShell().id == 'autotag':
        print 'Exiting autotag shell.'
        Shell.closeShell()
    else:
        print 'That doesn\'t do anything right now.'

def cmd_this(lbuf):
    if Shell.curShell().id == 'autotag':
        plv.cur_autotag_index -= 1
        increment_autotag_index()
    else:
        addMacro('/back 0')

def cmd_cache(buf):
    pcr = parseCmdHelper(buf[0])
    l = len(pcr.terms)
    if l != 1:
        fail = True
    else:
        try:
            if pcr.terms[0] == 'all':
                rrhelper = plv.rr
                fail = (len(plv.rr) == 0)
            else:
                n = int(pcr.terms[0])
                rrhelper = [plv.rr[n-1]]
                fail = False
        except:
            fail = True
    if fail:
        print 'Usage: cache <n> stores a local copy of nth result'
        return
    os.system('mkdir -p "'+plv.LOCALSONGSPATH+'/cache"')
    for song in rrhelper:
        if os.path.exists(os.path.join(plv.LOCALSONGSPATH, 'cache', os.path.split(song.data['fn'])[1]))\
        or os.path.exists(os.path.join(plv.LOCALSONGSPATH, os.path.split(song.data['fn'])[1])):
            print 'File already in local songs.'
        else:
            s = 'cp "'+song.data['fn']+'" "'+plv.LOCALSONGSPATH+'/cache"'
            print s
            os.system(s)
    print 'Done.'
    
#assuming a string (not Tag object) and a list of Song objects are passed in.
def doTag(tname, songs):
    tname = getAlias(tname)
    if '"' in tname or "'" in tname:
        print 'Bad tag name.'
        return
    try:
        t = Tag.tagsByName[tname]
    except:
        print 'New tag: '+tname
        t = Tag(tname)
        plv.tags.append(t)
        Tag.tagsByName[tname] = t
        invalidate()
    plv.lastTag = t
    print 'Applying tag: '+tname
    invalidatedAlready = False
    ctr = 0
    for song in songs:
        plv.didAnything = True
        if t in plv.tags:
            if song not in t.data['songs']:
                t.data['songs'].append(song)
                song.data['tags'].append(t)
                ctr += 1
                if not invalidatedAlready:
                    invalidate(t)
                    invalidatedAlready = True
        else:
            #this can be legitimately hit if you kill a tag, then make it again in the same session
            invalidate()
            t.data['songs'].append(song)
            song.data['tags'].append(t)
            ctr += 1
            plv.tags.append(t)
    print 'Applied tag to '+str(ctr)+' items.'

def cmd_tag(buf):
    plv.lastCmdWasSearch = False
    pcr = parseCmdHelper(buf[0])
    l = len(pcr.terms)
    if l == 2:
        try:
            n = int(pcr.terms[0])
            rrhelper = [plv.rr[n-1]]
        except:
            rrhelper = plv.rr
    else:
        rrhelper = plv.rr
    tname = pcr.terms[l-1].lower()
    try:
        n = int(tname)
        print 'Please don\'t use numbers as tags.'
    except:
        doTag(tname, rrhelper)

def cmd_same(buf):
    if plv.lastTag != None:
        cmd_tag([plv.lastTag.data['name']])
    else:
        print 'No previous tag to duplicate.'

def cmd_log(buf):
    print 'Saving & opening log file.'
    saveLog()
    os.popen(plv.notepad+' '+plv.cmdLogFile)

def cmd_kill(buf):
    args = buf[0].lower().split(' ')
    tname = getAlias(args[0])
    tag = Tag.tagsByName.get(tname, None)
    if tag != None:
        noInvalidate = len(args) == 2 and args[1] == '-i'
        killTag(tag, not noInvalidate)
    else:
        print 'Tag doesn\'t exist.'

def cmd_ds(buf):
    if buf[0] != '':
        plv.directorySearch = True
        print 'Directory search flag ON.'
        addMacro(buf[0])
        plv.continueFlag = True
        return
    plv.allowRefine = False
    if plv.directorySearch:
        print 'Directory search flag OFF.'
    else:
        print 'Directory search flag ON.'
    plv.directorySearch = not plv.directorySearch

def cmd_pp(buf):
    addMacro(buf[0]+';/p 1')
    
def cmd_p(buf):
    nosortFlag = (buf[0] == '--nosort')
    bufSplit = buf[0].split(' ')
    quickFlag = False
    if '--quick' in bufSplit:
        quickFlag = True
        bufSplit.remove('--quick')
        buf[0] = ' '.join(bufSplit)
    playAll = (len(buf[0]) == 0 or nosortFlag)
    try:
        if playAll:
            num = 0
        else:
            tname = getAlias(buf[0])
            if tname in Tag.tagsByName:
                tag = Tag.tagsByName[tname]
            else:
                tag = None
            if tag != None:
                if not quickFlag:
                    addMacro('/show '+buf[0]+';/p')
                else:
                    playPlaylist(opj(plv.ROOTDIR, plv.tagToPlaylist[tname]), plv.itunes_flag)
                plv.continueFlag = True
                return
            else:
                num = int(buf[0])-1
    except:
        print 'Invalid selection.'
        plv.continueFlag = True
        return
    if playAll and plv.lenrr > 0 and not plv.directorySearch:
        if playSongs(plv.rr, not nosortFlag, plv.itunes_flag):
            print 'Playing files.'
        else:
            print 'Could not play files.'
    elif num < plv.lenrr and num >= 0:
        if plv.directorySearch:
            addMacro('/ds;/cfds on;"'+plv.rr[num].data['fn']+'";/cfds off;/p --nosort')
            plv.continueFlag = True
            return
        if playSong(plv.rr[num], not nosortFlag, plv.itunes_flag):
            print 'Playing file '+plv.rr[num].data['fn']
        else:
            print 'Could not play file.'
    else:
        print 'Invalid selection.'

def cmd_dates(buf):
    if plv.lenrr == 0:
        print 'Nothing in selection.'
    ctr = 1
    for r in plv.rr:
        s = plv.rr.data['mtime']
        if s != plv.cZeroTime:
            s = dateTimeStr(s)
        else:
            s = ''
        print bracketNum(ctr) + s
        ctr += 1

def burn_options(optionlist, s):
    l = s.split(' ')
    return ' '.join([x for x in l if x not in optionlist])

def cmd_dir(buf):
    optionlist = ['--local','-l']
    parsed, optionlist = parseCmdWithOptions(buf[0], optionlist)
    uselocal = not plv.directorySearch and ('--local' in optionlist or '-l' in optionlist)
    if uselocal:
        print 'Using a local copy.'
    if plv.lenrr < 1:
        print 'Need a file selected.'
        plv.continueFlag = True
        return
    n = -1
    try:
        n = int(parsed[0])-1
    except:
        pass
    if n < 0 or n > plv.lenrr-1:
        print 'Bad index, defaulting to first element.'
        n = 0
    if not uselocal:
        s = plv.rr[n].data['fn']
    else:
        s = plv.rr[n].data['locals'][0]
    if plv.directorySearch:
        os.system('open "'+os.path.dirname(s)+'"')
        print 'Showing directory.'
    else:
        os.system('open "'+os.path.dirname(s)+'"')
        print 'Showing parent directory.'

def cmd_rn(buf):
    names = parseCmd(buf[0])
    if len(names) != 2:
        print 'Invalid rename operation (need two tag names).'
    elif names[0] not in Tag.tagsByName:
        print 'Tag doesn\'t exist.'
    elif names[1] in Tag.tagsByName:
        print 'Target tag already exists.'
    else:
        src = names[0]
        dst = names[1]
        plv.didAnything = True
        invalidate()
        tag = Tag.tagsByName[src]
        tag.data['name'] = dst
        Tag.tagsByName[dst] = tag
        del Tag.tagsByName[src]
        print 'Renamed tag.'

def cmd_move(buf):
    if plv.lenrr != 1:
        print 'You need exactly 1 element in the results list to move.'
        plv.continueFlag = True
        return
    shortDst = parseCmd(buf[0])
    if len(shortDst) != 1:
        print 'You need exactly 1 argument (destination file) to move.'
        plv.continueFlag = True
        return
    src = plv.rr[0].data['fn']
    tempDir = os.path.dirname(src) + plv.cSep
    tempExt = src[src.rfind('.'):]
    dst = tempDir + shortDst[0] + tempExt
    moveFile(src, dst)

def fmove_helper(curResult, shortDst):
    src = curResult.data['fn']
    x = os.path.split(src)
    tempDir = opj(plv.GENRESPLITPATH, shortDst)
    dst = opj(tempDir, x[1])
    moveFile(src, dst)

def cmd_fmove(buf):
    if plv.lenrr != 1:
        print 'You need exactly 1 element in the results list to move.'
        plv.continueFlag = True
        return
    shortDst = parseCmd(buf[0])
    curResult = plv.rr[0]
    fmove_helper(curResult, shortDst)
    
def cmd_banish(buf):
    for song in plv.rr:
        fn = song.data['fn']
        banishFile(fn)
    print 'Banished '+str(plv.lenrr)+' files.'

def cmd_rm(buf):
    tagName = getAlias(buf[0].lower())
    if tagName not in Tag.tagsByName:
        print 'Tag doesn\'t exist.'
    elif plv.rr == []:
        print 'No files (from search) to modify.'
    else:
        tag = Tag.tagsByName[tagName]
        invalidate(tag)
        ctr = 0
        for song in plv.rr:
            if tag in song.data['tags']:
                removeTagFromSong(tag, song)
                ctr += 1
        print 'Removed tag from '+str(ctr)+' entries.'
            
def cmd_show(buf):
    if plv.directorySearch:
        print 'Can\'t do this in a directory search.'
        plv.continueFlag = True
        return
    tagName = getAlias(buf[0].lower())
    if tagName not in Tag.tagsByName:
        print 'Tag doesn\'t exist.'
    else:
        plv.orderASpecialSearch = True
        plv.rr = Tag.tagsByName[tagName].data['songs']

def cmd_s(buf):
    if Shell.curShell().id == 'autotag':
        increment_autotag_index()
    else:
        cmd_show(buf)

def cmd_fwd(buf):
    traverseCmd(buf[0], 1)
    
def cmd_back(buf):
    traverseCmd(buf[0], -1)

def cmd_list(buf):
    print '\t'.join(tagsToNames(plv.tags))

def cmd_tags(buf):
    ctr = 0
    if plv.rr != []:
        for song in plv.rr:
            ctr += 1
            print bracketNum(ctr) + tagListToString(song.data['tags'])
    else:
        print 'Nothing in selection.'
        
def cmd_alias(buf):
    args = parseCmd(buf[0])
    if len(args) != 2:
        print 'Invalid arguments: must have exactly 2.'
        plv.continueFlag = True
        return
    if args[1] in Tag.tagsByAlias:
        print 'Alias already used.'
        plv.continueFlag = True
        return
    if args[1] in Tag.tagsByName:
        print 'Tag name already used.'
        plv.continueFlag = True
        return
    tag = Tag.tagsByName.get(args[0], None)
    if tag == None:
        print 'Invalid existing tag name.'
        plv.continueFlag = True
        return
    if tag.addAlias(args[1]):
        plv.aliasesChanged = True
        print 'Added alias.'
        
def cmd_wipe(buf):
    wipePlaylists()

def cmd_inv(buf):
    invalidate()
    print 'Invalidated everything.'
    
def cmd_w(buf):
    writetags()

def cmd_sl(buf):
    showSearchList()

def cmd_backup(buf):
    doBackup(buf)
    
def cmd_check(buf):
    checkIfFilesExist(plv.lines)

def cmd_new(buf):
    try:
        n = int(buf[0])
    except ValueError:
        n = 10
    addMacro('/kill newest -i;/newhelper '+str(n)+';/tag newest')
    
def cmd_newhelper(buf):
    try:
        n = int(buf[0])
    except ValueError:
        n = 10
    plv.rr = plv.lines
    # exclude albums
    plv.rr = filter(lambda x: plv.cSep+'+ Albums'+plv.cSep not in x.data['fn'], plv.rr)
    print 'Non-album songs from less than '+str(n)+' days ago:'
    newr = filter(lambda x: fileIsNew(x.data['fn'], n), plv.rr)
    if newr != []:
        plv.orderASpecialSearch = True
        plv.rr = newr[:]
    else:
        print 'No results. Reverting to last search.'

def cmd_tap(buf):
    addMacro('/rating -f 1')

def cmd_rating(buf):
    #floor option
    floorFlag = False
    if '-f ' in buf[0]:
        buf[0] = buf[0].replace('-f ','',1)
        floorFlag = True
    parsed = parseCmd(buf[0])
    bl = len(parsed)
    try:
        if bl == 1:
            rrIndex = -1
            n = float(parsed[0])
            pickList = plv.rr
        else:
            rrIndex = int(parsed[0])
            n = float(parsed[1])
            pickList = [plv.rr[rrIndex-1]]
    except:
        print 'Invalid input.'
        return
    for r in pickList:
        oldrating = r.data['rating']
        name = r.data['fn']
        cn = n
        if floorFlag:
            cn = max(n, oldrating)
        if oldrating != 0:
            print name+': changed from '+ratingString(oldrating)+' to '+ratingString(cn)+'.'
        else:
            print name+': new rating '+ratingString(cn)+'.'
        r.data['rating'] = cn
        plv.ratingdataChanged = True

def cmd_i(buf):
    if plv.itunes_flag:
        print 'itunes flag OFF.'
    else:
        print 'itunes flag ON.'
    plv.itunes_flag = not plv.itunes_flag

def ratings_zero_map(x):
    return ratingToString(rating(x))

def cmd_ratings(buf):
    printResults(map(ratings_zero_map, plv.rr))

def ageBetween(fn, a, b):
    td = fileAge(fn)
    return td >= a and td <= b

def cmd_time(buf):
    default_time_const = 30
    try:
        includeAlbums = False
        aroundAFile = False
        noPlayAfter = False
        
        optionlist = ['-ia', '-np']
        inputl, optionlist = parseCmdWithOptions(buf[0], optionlist)
        
        if '-ia' in optionlist:
            print 'Including album songs.'
            includeAlbums = True
        if '-np' in optionlist:
            print 'Not playing after search.'
            noPlayAfter = True
            
        nthResult = 1
        if len(inputl) > 0 and inputl[0] == 'a':
            aroundAFile = True
            inputl = inputl[1:]
            try:
                nthResult = int(inputl[0])
                inputl = inputl[1:]
                if nthResult < 1 or nthResult > plv.lenrr:
                    raise
            except:
                nthResult = 1
                print 'Bad arg for time-around, using first result.'
        
        if aroundAFile:
            if len(inputl) > 0:
                try:
                    delta = int(inputl[0])
                    if delta < 0:
                        raise
                except:
                    delta = default_time_const/2
            else:
                delta = default_time_const/2
            a = fileAge(plv.rr[nthResult-1].data['fn']).days - delta
            b = a + delta*2
            print 'Printing songs around result #'+str(nthResult)+'.'
        else:
            a = int(inputl[0])
            try:
                b = int(inputl[1])
            except:
                b = a + default_time_const
            if a > b:
                t = a
                a = b
                b = t
    except:
        print 'Invalid input.'
        return  
    print 'Playing songs between '+str(a)+' and '+str(b)+' days old.'
    if includeAlbums:
        plv.rr = plv.lines[:]
    else:
        plv.rr = filter(lambda x: plv.ALBUMPATH not in x.data['fn'], plv.lines)
    a = datetime.timedelta(days=a)
    b = datetime.timedelta(days=b)
    plv.rr = filter(lambda x: ageBetween(x.data['fn'], a, b), plv.rr)
    plv.orderASpecialSearch = True
    if not noPlayAfter:
        addMacro('/p')
    
def fnFilter_nonSet(song):
    return not song.data['fn'].startswith(plv.SETPATH)

def cmd_save(buf):
    #excludes sets from result
    inputl = parseCmd(buf[0])
    if len(inputl) != 1 or inputl[0].strip() == '':
        print 'Invalid input. (needs one nonempty arg)'
        return
    dst = opj(plv.SAVEDPLAYLISTPATH, inputl[0])+plv.plExt
    writePls(dst, filter(fnFilter_nonSet, plv.rr), True)
    print 'Saved playlist to: '+dst
    
def fnFilter_ratingOverN(song, n):
    return song.data['rating'] >= n

def cmd_over(buf):
    try:
        n = int(buf[0])
    except ValueError:
        n = 1
    print 'Playing songs with rating >= '+str(n)
    plv.rr = filter(lambda x: fnFilter_ratingOverN(x, n), plv.lines)
    plv.orderASpecialSearch = True
    
def cmd_cfds(buf):
    if buf[0] == 'on':
        plv.comesFromDirectorySearch = True
        print 'cfds ON'
    elif buf[0] == 'off':
        plv.comesFromDirectorySearch = False
        print 'cfds OFF'
        
def cmd_info(buf):
    print '=== INFO ==='
    print ''
    print 'allowRefine: '+boolstr(plv.allowRefine)
    print 'comesFromDirectorySearch: '+boolstr(plv.comesFromDirectorySearch)
    print 'continueFlag: '+boolstr(plv.continueFlag)
    print 'didAnything: '+boolstr(plv.didAnything)
    print 'directorySearch: '+boolstr(plv.directorySearch)
    print 'invalidateAllTags: '+boolstr(plv.invalidateAllTags)
    print 'lastCmdWasSearch: '+boolstr(plv.lastCmdWasSearch)
    print 'lastTag: '+lastTagToStr()
    print 'needRewriteDirfill: '+boolstr(plv.needRewriteDirfill)
    print 'orderASpecialSearch: '+boolstr(plv.orderASpecialSearch)
    print 'ratingdataChanged: '+boolstr(plv.ratingdataChanged)
    print 'rptr: '+str(plv.rptr)
    
def cmd_guess(buf):
    optionlist = ['-a','-m']
    parsed, optionlist = parseCmdWithOptions(buf[0], optionlist)
    APPLYING_TAGS = False
    MOVING_FILES = False
    if '-a' in optionlist:
        print 'OPTION -a: Applying tags'
        APPLYING_TAGS = True
    if '-m' in optionlist:
        print 'OPTION -m: Moving files'
        MOVING_FILES = True
    #else:
    #    print 'Bad arguments to "guess".'
    #    return
    if len(plv.rr) == 0:
        print 'Need at least 1 result to process.'
        return
    #print 'Guess reached here successfully.'
    for curResult in plv.rr:
        d = {}
        similarFileCount = 0
        fnk = curResult.data['sk']
        artist = curResult.getArtistAndTitle()[0]
        didFindTag = False
        if artist != '':
            for key in plv.songDict['sk']:
                if artist in key and plv.songDict['sk'][key] != curResult:
                    similarFileCount += 1
                    for t in plv.songDict['sk'][key].data['tags']:
                        tname = t.data['name']
                        if tname in d:
                            d[tname] += 1
                        else:
                            d[tname] = 1
            prelist = [(k, d[k]) for k in d]
            prelist.sort(key=operator.itemgetter(1), reverse=True)
            l = filter(lambda (a,b): float(b)/similarFileCount > 0.2, prelist)
            if len(l) != 0:
                print 'Artist: '+artist
                for k in prelist:
                    print '  '+k[0]+':'+str(k[1])
            for (k, v) in l:
                didFindTag = True
                #suggestedTagList.append(getTag(k))
                #print k
                if APPLYING_TAGS:
                    addTagToSong(getTag(k), curResult)
                if MOVING_FILES and doesGenreFolderExist(k):
                    #print k+' does, in fact, exist.'
                    print 'Moving file to genre folder: '+k
                    fmove_helper(curResult, k)
                    #addMacro('/fmove "'+k+'"')
                    break
                else:
                    pass
                    #print k+' doesn\'t exist.'
        if not didFindTag:
            pass
            #print 'No suitable tag guesses.'
        else:
            print 'Guessed tags: '+', '.join(map(operator.itemgetter(0), l))
            print ''

def cmd_dc(buf):
    killVLC()
    os.system('disk IPOD')
    addMacro('/ns')

def cmd_sys(buf):
    #don't parse buf[0]
    os.system(buf[0])

def cmd_msg(buf):
    if plv.USE_VLC_RC:
        os.system('echo '+buf[0]+' | nc -U '+plv.VLCSOCK)
    else:
        print 'Not using vlc rc interface, so nothing done.'

def cmd_m(buf):
    cmd_msg(buf)

def cmd_or(buf):
    inputl = parseCmd(buf[0])
    plv.orSearch = True
    plv.orderASearch = True
    plv.refinedSearch = True
    plv.continueFlag = False

#----

def boolstr(b):
    if b:
        return 'YES'
    else:
        return '-'

def lastTagToStr():
    if plv.lastTag == None:
        return '<None>'
    else:
        return plv.lastTag

def canRefine():
    return plv.allowRefine and len(plv.rr) > 0

def getSearchWords(x):
    x = x.replace(r'\ ', spaceHolderString)
    return map(lambda y: y.strip().replace(spaceHolderString, ' '), x.split(' '))

def parseCmdHelper(s, *flags):
    inQuote = False
    slashed = False
    negated = False
    inAssignment = False
    term = ''
    curAssignment = ''
    pcr = ParseCmdResult()
    pcr.careAboutNegs = 'pn' in flags
    pcr.terms = []
    pcr.negTerms = []
    for c in s:
        if slashed:
            term += c
            slashed = False
        elif c == '\\': #this is to backslash characters for command parsing. not part of windows filenames!
            slashed = True
        elif c == '"':
            inQuote = not inQuote
        elif c == ' ':
            if inQuote:
                term += c
            else:
                if inAssignment:
                    pcr.params[curAssignment] = term
                elif pcr.careAboutNegs and negated:
                    pcr.negTerms.append(term)
                else:
                    pcr.terms.append(term)
                term = ''
                negated = False
                inAssignment = False
        elif c == '-':
            if inQuote:
                term += c
            else:
                negated = True
        elif c == '=':
            curAssignment = term
            term = ''
            inAssignment = True
        else:
            term += c
    if inQuote:
        print 'You missed an endquote, so I put it in. :('
    if term != '':
        if inAssignment:
            pcr.params[curAssignment] = term
        elif pcr.careAboutNegs and negated:
            pcr.negTerms.append(term)
        else:
            pcr.terms.append(term)
        term = ''
        negated = False
        inAssignment = False
    return pcr

#parsing searches and tag/rm
#returns a list
def parseCmd(s, *flags):
    pcr = parseCmdHelper(s, *flags)
    if pcr.careAboutNegs:
        return pcr.terms, pcr.negTerms
    else:
        return pcr.terms
    
def parseCmdWithOptions(s, optionlist, *flags):
    ol = filter(lambda x: x in s, optionlist)
    s = burn_options(ol, s)
    return parseCmd(s, *flags), ol

#parsing within-list numerical selections
def parseSelect(s, mini, maxi):
    ranges = map(lambda x: x.strip(), s.split(','))
    ret = []
    ctr = 0
    for ran in ranges:
        ctr += 1
        if ran == '' or ran == '-':
            continue
        if ran[0] == '-':
            parity = False
            ran = ran[1:]
            if ctr == 1:
                ret = list(range(mini-1, maxi))
        else:
            parity = True
        try:
            if '-' not in ran:
                n = int(ran)
                if n >= mini and n <= maxi:
                    if parity:
                        ret.append(int(ran)-1)
                    else:
                        ret.remove(int(ran)-1)
                else:
                    raise
            else:
                bounds = ran.split('-')
                lb = max(mini-1, int(bounds[0])-1)
                ub = min(maxi, int(bounds[1]))
                if parity:
                    ret += range(lb, ub)
                else:
                    y = range(lb, ub)
                    ret = filter(lambda x: x not in y, ret)
        except:
            print 'Bad selection.'
            ret = []
    return ret

def wipePlaylists():
    l = listdir(plv.ROOTDIR)
    for fn in l:
        if fn.endswith(plv.plExt):
            os.system('rm "'+opj(plv.ROOTDIR,fn)+'"')
    print 'Wiped playlists.'
    invalidate()

def removeTagFromSong(tag, song, invalidateFlag=True):
    try:
        song.data['tags'].remove(tag)
    except:
        pass
    try:
        tag.data['songs'].remove(song)
    except:
        pass
    if tag.data['songs'] == [] and invalidateFlag:
        invalidate()
        
def addTagToSong(tag, song, invalidateFlag=True):
    if tag not in song.data['tags']:
        song.data['tags'].append(tag)
        if invalidateFlag:
            invalidate(tag)
    if song not in tag.data['songs']:
        tag.data['songs'].append(song)
        if len(tag.data['songs']) == 1 and invalidateFlag:
            invalidate()

def killTag(tag, invalidateFlag = True):
    tname = tag.data['name']
    for song in plv.songs:
        if tag in song.data['tags']:
            removeTagFromSong(tag, song, invalidateFlag)
    if tag in plv.tags:
        plv.didAnything = True
        if invalidateFlag:
            plv.tags.remove(tag)
            invalidate()
        else:
            print 'No-invalidate flag set: '+tname
        print 'Killed tag: '+tname
    else:
        print 'Tag doesn\'t exist.'
    
def printResults(res):
    srcCtr = 0
    for r in res:
        try:
            print bracketNum(srcCtr+1)+r
            srcCtr += 1
        except UnicodeEncodeError:
            print plv.cBadStr
    if srcCtr > 0:
        print ''
    if plv.directorySearch:
        print 'This is an ALBUM search.'
    print 'Found '+str(srcCtr)+' items.'

def stringOr(s, pos, neg):
    s = s.lower()
    for p in pos:
        if p != '' and p in s:
            return True
    for n in neg:
        if n != '' and n not in s:
            return True
    return False

def orFilterPosNeg(pos, neg):
    return lambda x: stringOr(x.data['fn'], pos, neg)

def stringContainsPosNotNeg(s, pos, neg):
    s = s.lower()
    for p in pos:
        if p != '' and p not in s:
            return False
    for n in neg:
        if n != '' and n in s:
            return False
    return True

def filterPosNeg(pos, neg):
    return lambda x: stringContainsPosNotNeg(x.data['fn'], pos, neg)

def orderSearch(x, res, b):
    if res != []:
        if x == '':
            filterPN = lambda x: True
        else:
            words, negwords = parseCmd(x, 'pn') #differentiate between positive and negative search terms
            if b:
                filterPN = orFilterPosNeg(words, negwords)
            else:
                filterPN = filterPosNeg(words, negwords)
        if plv.comesFromDirectorySearch or plv.directorySearch:
            res = filter(filterPN, res)
        else:
            #print filter(filterPN, res)
            res = sorted(filter(filterPN, res), key=rating, reverse=True)
    printResults(mapSongsToNames(res))
    if x != '':
        plv.cmdLog.append(x)
    return res

def rating(song):
    return song.data['rating']
                                                
def grabInput(cq):
    notfirst = True
    shellString = Shell.curShell().id + '>> '
    if cq == []:
        instr = raw_input(shellString)
        cq += instr.split(';')
        notfirst = False
    x = cq.pop(0).strip()
    if notfirst:
        print shellString+x
    return x

def main():
    os.system('echo "\033]0;= PLAYLISTMAKER =\007"')
    if not checkLock():
        waitAtEnd()
        return
    if os.path.exists(plv.historyFile):
        readline.read_history_file(plv.historyFile)
        print 'History contains '+`readline.get_current_history_length()`+' entries.'
    else:
        print 'History file not found.'
    plv.NOIPODMODE = not os.path.exists(plv.ROOTDIR)
    os.system(os.path.join(plv.PLMAKERDIR,'killdotfiles.py'))
    plv.dirFillLines = dirFillToList()
    timelist = [time.clock()]
    plv.lines = plv.songs
    for l in plv.dirFillLines:
        sd = SongData(l[0], l[1])
        plv.songs.append(sd)
        #use dirfill's filename sort key (index 1)
        plv.fileNames2sortKeys[l[0]] = l[1]
        #use dirfill's creation date if available (index 2)
        if len(l) >= 3:
            td = invDateTimeStr(l[2])
            sd.data['mtime'] = td
            plv.fileNames2Dates[l[0]] = td
    plv.sortKeys2fileNames = dict((v,k) for (k,v) in plv.fileNames2sortKeys.items())
    readRatingData()
    readtags()
    fillTagAliases()
    readDirs()
    readLocalSongs()
    
    if plv.MENU_AVAILABLE:
        import menu
        if len(sys.argv) > 1 and sys.argv[1] == '-menu':
            argv = sys.argv[0:1]
            if len(sys.argv) > 2:
                argv += sys.argv[2:]
            menu.main(argv)
            sys.exit(0)
    
    if not plv.NOIPODMODE and needAutoBackup():
        print 'Doing autobackup.'
        doBackup(['-doe'])
    else:
        if plv.NOIPODMODE:
            print 'No IPOD found, skipping backup. (!!!)'
        else:
            print 'No autobackup needed.'
    
    Shell.openShell('')
    buf = [None]
    firstRun = True
    while True:
        if firstRun:
            firstRun = False
            try:
                #preprocess code
                l = clean(fread(plv.preprocess_file))
                if l != []:
                    addMacro(';'.join(l))
                    print 'Using preprocess file...'
            except:
                pass
        else:
            plv.rr = readRes()
            print ''
        plv.lenrr = len(plv.rr)
        x = grabInput(plv.cmdQueue)
        #disable lowercasing for these commands
        b = False
        b = reduce(lambda a, y: a and not isTheCommand(x, y), [True] + plv.no_lowercase_conversion_commands)  
        if b:
            x = x.lower()
        if x in plv.quitlist:
            if x == '/ns':
                plv.saveAtEnd = False
            break
        plv.orderASearch = False
        plv.refinedSearch = False
        plv.orderASpecialSearch = False
        doASelection = False
        plv.continueFlag = False
        plv.orSearch = False
        if x != '': #god what a disgusting hack
            print ''
        else:
            continue
        #command-processing engine
        cmdName = getCommandFromInput(x)
        cmd = findCmd(cmdName)
        if cmd:
            doTheCommand(x, cmdName, buf)
            if plv.continueFlag:
                continue
        #commands not yet migrated
        elif x in plv.helplist:
            print '  - HELP -'
            for c in plv.commandlist:
                print '\n'+c.asStr()
        elif x[0] == ',':
            if not canRefine():
                print 'Can\'t refine this search.'
                continue
            else:
                sele = x[1:]
                doASelection = True
        elif x[0] == '.':
            x = x[1:]
            if not canRefine():
                print 'Can\'t refine this search.'
                continue
            else:
                plv.orderASearch = True
                plv.refinedSearch = True
        elif x[0] == '/':
            print 'Failed command?'
        elif Shell.curShell().id == 'autotag':
            autotag_handler(x)
        else:
            plv.orderASearch = True
        if doASelection:
            if plv.rr != []:
                ps = parseSelect(sele, 1, plv.lenrr)
                if plv.directorySearch and len(ps) == 1:
                    addMacro('/ds;/cfds on;"'+plv.rr[ps[0]].data['fn']+'";/cfds off')
                    continue
                elif ps != []:
                    plv.orderASpecialSearch = True
                    plv.rr = [plv.rr[i] for i in ps]
                else:
                    print 'No results. Reverting to last search.'
            else:
                print 'Can\'t select from nothing.'
        if plv.orderASpecialSearch:
            plv.orderASearch = True
            plv.refinedSearch = True
            x = ''
        if plv.orderASearch:
            if not plv.refinedSearch:
                if plv.directorySearch:
                    plv.rr = plv.dirlist
                else:
                    plv.rr = plv.lines
            newSearch(orderSearch(x, plv.rr, plv.orSearch), x)#that last part is so /sl can see the command that caused that search
            plv.allowRefine = True
    writeHistory()
    if not nothingToDo() and plv.saveAtEnd:
        print '\nWriting tags & playlists...'
        writetags()
    else:
        print '\nNothing was done. No need to save.'
    saveLog()
    if plv.AUTO_EXPORT:
        print 'Auto-exported playlistmaker data...',
        subprocess.call([opj(plv.PLMAKERDIR, 'export.py'), '-s'])
        print 'done.'
    print 'Bye!'
    unlock()
    waitAtEnd()
    
if __name__ == '__main__':
    main()
