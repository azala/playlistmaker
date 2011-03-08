import os, datetime, shutil, time, subprocess, menu, plutil
from command import *
import plvars as plv
from plutil import *

class ParseCmdResult:
    def __init__(self):
        self.careAboutNegs = False
        self.terms = []
        self.negTerms = []
        #self.flags = []
        self.params = {}

def fileIsNewAndExists(fn, n):
    try:
        return fileIsNew(fn, n)
    except:
        print 'File couldn\'t be evaluated:'
        tryPrint(fn, '  ')
        plv.orphans.append(fn)
        return False

def nothingToDo():
    return not plv.invalidateAllTags and \
        plv.invalidateTheseTags == [] and \
        plv.move_file_queue == [] and \
        plv.orphans == [] and \
        plv.needRewriteDirfill == False and \
        plv.ratingdataChanged == False

def removeAllTagsForFile(fn):
    if fn in plv.taglists: 
        for s in plv.taglists[fn]:
            invalidate(s)
            plv.playlists[s].remove(fn)
            if plv.playlists[s] == []:
                invalidate()
        del plv.taglists[fn]

def removeTagForFile(fn, t):
    invalidate(t)
    ctr = 0
    if fn in plv.taglists and t in plv.taglists[fn]:
        plv.taglists[fn].remove(t)
        plv.playlists[t].remove(fn)
        if plv.playlists[t] == []:
            invalidate()
    ctr += 1
    return ctr

def checkIfFilesExist(l):
    found = False
    for fn in l:
        if not os.path.isfile(fn):
            tryPrint('Not file: '+fn,'')
            plv.orphans.append(fn)
            found = True
    if not found:
        print 'No problems with dirfill.'

def invalidate(t = None):
    if t == None:
        if plv.invalidateAllTags:
            return
        plv.invalidateAllTags = True
        plv.invalidateTheseTags = []
        print'Invalidated all tags.'
    elif t not in plv.invalidateTheseTags and not plv.invalidateAllTags:
        print'Invalidated tag: '+t
        plv.invalidateTheseTags.append(t)

def revalidate():
    plv.invalidateTheseTags = []
    plv.invalidateAllTags = False

def applyOrphans():
    for fn in plv.orphans:
        if not os.path.isfile(fn):
            removeAllTagsForFile(fn)
            removeFileFromDirfill(fn) 
    if plv.orphans == []:
        pass
    else:
        print 'Removed data for orphans.'
    plv.orphans = []

def removeFileFromDirfill(fn):
    plv.dirFillLines = filter(lambda x: x[0] != fn, plv.dirFillLines)
    plv.needRewriteDirfill = True

def rewriteDirfillIfNeeded():
    if plv.needRewriteDirfill:
        df = open(plv.DIRFILLPATH, 'wb')
        for l in list(map(lambda x: '\t'.join(x)+'\r\n', plv.dirFillLines)):
            df.write(l.encode('utf-8'))
        df.close()
        plv.needRewriteDirfill = False
        print 'Applied orphans to dirfill.txt.'

def readRatingData():
    for l in clean(fread(plv.ratingFile)):
        k, v = l.split('\t')
        plv.ratingdata[k] = int(v)
    print 'Loaded rating data.'
    
#---FILE MOVE
        
def moveFile(src, dst, banish = False):
    if src == dst:
        print 'Failed, both names are the same.'
        return
    for e in plv.move_file_queue:
        if e[2] == dst:
            print 'Failed, another file is going to move there.'
            return
    try:
        subprocess.check_call(['move', src, dst], shell=True)
    except (subprocess.CalledProcessError, WindowsError) as e:
        print 'Move failed: '+str(e)
        return
    #sort key update
    srcKey = plv.fileNames2sortKeys[src]
    del plv.sortKeys2fileNames[srcKey]
    del plv.fileNames2sortKeys[src]
    if not banish:
        dstKey = plv.fileNames2sortKeys[dst] = pathToFileNameKey(dst) # need error checking on this
        plv.sortKeys2fileNames[dstKey] = dst
        plv.fileNames2Dates[dst] = plv.fileNames2Dates[src]
        #search history update
        replaceResult(src, dst)
    del plv.fileNames2Dates[src]
    #taglists and playlists update
    if src in plv.taglists:
        srcTags = plv.taglists[src]
        for t in srcTags:
            invalidate(t)
            if not banish:
                plv.playlists[t] = [dst if x == src else x for x in plv.playlists[t]]
            else:
                plv.playlists[t].remove(src)
        if not banish:
            plv.taglists[dst] = plv.taglists[src][:]
        del plv.taglists[src]
    #all filenames database update
    plv.lines.remove(src)
    if not banish:
        plv.lines.append(dst)
    #update dirfill.txt
    if not banish:
        replacedDst = False
        for i, item in enumerate(plv.move_file_queue):
            if item[2] == src:
                replacedDst = True
                print 'Replaced a previous move action.'
                plv.move_file_queue[i][2] = dst
                plv.move_file_queue[i][3] = dstKey
                break
        if not replacedDst:
            plv.move_file_queue.append([src, srcKey, dst, dstKey])
            print 'Moved "'+src.rpartition('\\')[2]+'" to "'+dst.rpartition('\\')[2]+'".'

def applyMoveFileQueue():
    replaceDirFillEntry(plv.move_file_queue)
    plv.move_file_queue = []

def banishFile(fn):
    moveFile(fn, plv.DONTWANTPATH, True)
    
#---SEARCH RESULTS



def newSearch(newResults):
    plv.resultHistory = plv.resultHistory[-1*plv.maxStoredResults+1:] + [newResults]
    plv.resultHistory_DSFlag = plv.resultHistory_DSFlag[-1*plv.maxStoredResults+1:] + [plv.directorySearch]
    #plv.resultHistory_NoSortFlag = plv.resultHistory_NoSortFlag[-1*plv.maxStoredResults+1:] + [plv.nosort]
    plv.rptr = len(plv.resultHistory)-1

def replaceResult(src, dst):
    for rh in plv.resultHistory:
        if dst == plv.DONTWANTPATH:
            rh = list(filter(lambda x: x != src, rh))
        else:
            for i in range(0, len(rh)):
                if rh[i] == src:
                    rh[i] = dst
    
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
            printResults(readRes())
        else:
            print 'Couldn\'t move '+ba_string+' '+str(s)+' searches.'
    except:
        print 'Bad argument.'

def writeRes(x):
    plv.resultHistory[plv.rptr] = x

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
        print pref + str(len(plv.resultHistory[i]))
        
def getAlias(k, boo = True):
    if k in plv.tag_aliases:
        if boo:
            print 'Using alias "'+plv.tag_aliases[k]+'".'
        return plv.tag_aliases[k]
    else:
        return k
        
def defaultListFilter(l):
    return filter(lambda x: x != '', map(lambda x: x.strip().decode('utf-8'), l))
        
def fillTagAliases():
    inf = open(plv.tag_aliasfile, 'rb')
    aliasLines = defaultListFilter(inf.readlines())
    inf.close()
    aliasLines = map(lambda x: x.split('\t'), aliasLines)
    for line in aliasLines:
        for k in line[1:]:
            plv.tag_aliases[k] = line[0]
        
def getPriorityTags():
    inf = open(plv.tag_priorityfile, 'rb')
    ptags = list(filter(lambda x: x != '', map(lambda x: x.strip().decode('utf-8'), inf.readlines())))
    inf.close()
    inf = open(plv.tag_indexfile, 'rb')
    tags = list(filter(lambda x: x != '' and x not in ptags, map(lambda x: x.strip().decode('utf-8'), inf.readlines())))
    inf.close()
    tags.sort()
    return ptags, tags

def plkeysSorted():
    head = plv.ptag_index
    tail = list(filter(lambda x: x not in plv.ptag_index, plv.plkeys))
    tail.sort()
    return list(filter(lambda x: x in plv.playlists, head + tail))

def doBackup(buf = ['']):
    try:
        params = parseCmd(buf)
    except:
        print 'Invalid input.'
    doE = '-doe' in params
    filelist = list(filter(lambda x: x.endswith('.txt'), listdir(plv.CDATAPATH)))
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
    plv.dirlist = clean(fread(plv.albumfile))
    
def readtags():
    tf = open(plv.tagfile, 'rb')
    rawtfLines = list(map(lambda x: x.decode('utf-8').strip().split('\t'), tf.readlines()))
    #tfLines = list(filter(lambda x: x[0] in lines, tfLines)) #x[0] is filename, lines is dirfill
    tfLines = []
    knownFileNames = []
    invalidateTheseLater = []
    ctr = 0
    for i in range(len(rawtfLines)-1, -1, -1):
        l = rawtfLines[i][:]
        if l[0] not in plv.lines: #if a filename from tagfile is not in dirfill
            print 'Filename not in directory?! (bug)'
            for t in l[1:]:
                invalidateTheseLater.append(t)
            tryPrint(l[0],'  ')
        elif l[0] in knownFileNames: #if a filename from tagfile was listed earlier in plv.tagfile
            ctr += 1
            tfLines.append(l)
            invalidate()
            print 'Duplicate filename:'
            tryPrint(l[0],'  ')
        else:
            ctr += 1
            tfLines.append(l)
            knownFileNames.append(l[0])
    print 'Imported '+str(ctr)+' tagged files.'
    tf.close()
    plv.ptag_index, tag_index = getPriorityTags()
    plv.plkeys = plv.ptag_index + tag_index
    if plv.plkeys == []:
        print 'Blank tag index file.'
        print 'Generating new playlist order.'
    for l in tfLines:
        for v in l[1:]:
            w = getAlias(v, False)
            if v != w:
                print 'Converting alias "'+v+'" to "'+w+'".'
                invalidate()
            v = w
            v = v.lower()
            if v in plv.playlists:
                if l[0] not in plv.playlists[v]:
                    plv.playlists[v] += [l[0]]
            else:
                plv.playlists[v] = [l[0]]
                if v not in plv.plkeys:
                    plv.plkeys.append(v)
            if l[0] in plv.taglists:
                if v not in plv.taglists[l[0]]:
                    plv.taglists[l[0]] += [v]
            else:
                plv.taglists[l[0]] = [v]
    for t in invalidateTheseLater:
        invalidate(t)
    print 'Read tags & playlists.'

#stuff you might search for:
#doWrite, writeout
def writetags():
    if nothingToDo():
        print 'Nothing was done. No need to save.'
        return
    if not os.path.exists(plv.ROOTDIR):
        print 'iPod missing ('+plv.ROOTDIR+').'
        return
    #----remove orphans
    applyOrphans()
    rewriteDirfillIfNeeded()
    #----apply file movements
    applyMoveFileQueue()
    #----write tagfile
    tf = open(plv.tagfile, 'wb')
    for t in plv.taglists:
        if plv.taglists[t] != []:
            line = t+'\t'+'\t'.join(plv.taglists[t])
            tf.write((line+'\r\n').encode('utf-8'))
    tf.close()
    #----write playlists
    if plv.invalidateAllTags:
        wipePlaylists()
    ctr = 0
    gpl_ctr = 0
    tif = open(plv.tag_indexfile, 'wb')

    if plv.invalidateAllTags:
        lenplkeys = len(plv.plkeys)
    else:
        lenplkeys = len(list(filter(lambda x: plv.playlists[x] != [] and x in plv.invalidateTheseTags, plv.plkeys)))

    for v in plkeysSorted():
        if plv.playlists[v] == []:
            continue
        tif.write((v+'\r\n').encode('utf-8'))
        gpl_ctr += 1
        if not plv.invalidateAllTags and v not in plv.invalidateTheseTags:
            continue
        pf = open(os.path.join(plv.ROOTDIR, '[%02d]'%gpl_ctr + v + plv.plExt), 'wb')
        plv.playlists[v].sort(key=lambda x: plv.fileNames2sortKeys[x])
        ctr += 1
        print 'Writing: ('+str(ctr)+'/'+str(lenplkeys)+') '+v
        for k in plv.playlists[v]:
            pf.write((k.replace(plv.ROOTDIR, '/').replace('\\','/')+'\r\n').encode('utf-8'))
        pf.close()
    tif.close()
    #write rating data
    if plv.ratingdataChanged:
        fwrite(unclean([k+'\t'+str(plv.ratingdata[k]) for k in plv.ratingdata]), plv.ratingFile)
        print 'Wrote rating data.'
    plv.ratingdataChanged = False
    print 'Done writing.'
    revalidate()

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
    return x.split(' ')[0][1:]

def doTheCommand(x, cmdShortString, lbuf = [None]):
    b = isTheCommand(x, cmdShortString, lbuf)
    if b:
        s = plv.FUNC_PREFIX+cmdShortString
        if s not in globals():
            print 'Failed command?'
        else:
            globals()[s](lbuf)
    return b

def cmd_this(lbuf):
    addMacro('/back 0')

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
    t = getAlias(pcr.terms[l-1].lower())
    if '"' in t or "'" in t:
        print 'Bad tag name.'
        return
    plv.lastTag = t
    print 'Applying tag: '+t
    #plv.rr = readRes()
    invalidatedAlready = False
    ctr = 0
    for r in rrhelper:
        plv.didAnything = True
        if t in plv.playlists:
            if r not in plv.playlists[t]:
                plv.playlists[t] += [r]
                ctr += 1
                if not invalidatedAlready:
                    invalidate(t)
                    invalidatedAlready = True
        else:
            invalidate()
            plv.playlists[t] = [r]
            ctr += 1
            plv.plkeys += [t]
        if r in plv.taglists:
           if t not in plv.taglists[r]:
                plv.taglists[r] += [t]
        else:
            plv.taglists[r] = [t]
    print 'Applied tag to '+str(ctr)+' items.'

def cmd_same(buf):
    if plv.lastTag != None:
        cmd_tag([plv.lastTag])
    else:
        print 'No previous tag to duplicate.'

def cmd_log(buf):
    print 'Saving & opening log file.'
    saveLog()
    os.popen(plv.notepad+' '+plv.cmdLogFile)

def cmd_kill(buf):
    args = buf[0].lower().split(' ')
    v = getAlias(args[0])
    noInvalidate = len(args) == 2 and args[1] == '-i'
    killTag(v, not noInvalidate)

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
    playAll = (len(buf[0]) == 0 or nosortFlag)
    try:
        if playAll:
            num = 0
        else:
            if getAlias(buf[0]) in plv.playlists:
                addMacro('/show '+buf[0]+';/p')
                plv.continueFlag = True
                return
            else:
                num = int(buf[0])-1
    except:
        print 'Invalid selection.'
        plv.continueFlag = True
        return
    if playAll and plv.lenrr > 0 and not plv.directorySearch:
        if playFiles(plv.rr, not nosortFlag):
            print 'Playing files.'
        else:
            print 'Could not play files.'
    elif num < plv.lenrr and num >= 0:
        if plv.directorySearch:
            addMacro('/ds;/cfds on;"'+plv.rr[num]+'";/cfds off;/p --nosort')
            plv.continueFlag = True
            return
        if playFile(plv.rr[num], not nosortFlag):
            print 'Playing file '+plv.rr[num]
        else:
            print 'Could not play file.'
    else:
        print 'Invalid selection.'

def cmd_dates(buf):
    if plv.lenrr == 0:
        print 'Nothing in selection.'
    ctr = 1
    for r in plv.rr:
        if r in plv.fileNames2Dates:
            s = dateTimeStr(plv.fileNames2Dates[r])
        else:
            s = ''
        print bracketNum(ctr) + s
        ctr += 1

def cmd_dir(buf):
    if plv.lenrr < 1:
        print 'Need a file selected.'
        plv.continueFlag = True
        return
    n = -1
    try:
        n = int(buf[0])-1
    except:
        pass
    if n < 0 or n > plv.lenrr-1:
        print 'Bad index: '+buf[0]+'\r\nDefaulting to first element.'
        n = 0
    if plv.directorySearch:
        os.system('explorer "'+plv.rr[n]+'"')
        print 'Showing directory.'
    else:
        os.system('explorer "'+plv.rr[n].rpartition('\\')[0]+'"')
        print 'Showing parent directory.'

def cmd_rn(buf):
    tags = parseCmd(buf[0])
    if len(tags) != 2:
        print 'Invalid rename operation (need two tag names).'
    elif tags[0] not in plv.playlists:
        print 'Tag doesn\'t exist.'
    elif tags[1] in plv.playlists:
        print 'Target tag already exists.'
    else:
        plv.didAnything = True
        invalidate()
        plv.playlists[tags[1]] = plv.playlists[tags[0]]
        del plv.playlists[tags[0]]
        for t in plv.taglists:
            if tags[0] in plv.taglists[t]:
                plv.taglists[t].remove(tags[0])
                plv.taglists[t].append(tags[1])
        for i in range(0, len(plv.plkeys)):
            if plv.plkeys[i] == tags[0]:
                plv.plkeys[i] = tags[1]
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
    src = plv.rr[0]
    tempDir = plv.rr[0].rpartition('\\')[0] + '\\'
    tempExt = '.' + plv.rr[0].rpartition('.')[2]
    dst = tempDir + shortDst[0] + tempExt
    moveFile(src, dst)

def cmd_fmove(buf):
    if plv.lenrr != 1:
        print 'You need exactly 1 element in the results list to move.'
        plv.continueFlag = True
        return
    shortDst = parseCmd(buf[0])
    if len(shortDst) != 1:
        print 'You need exactly 1 argument (destination directory) to move.'
        plv.continueFlag = True
        return
    src = plv.rr[0]
    x = plv.rr[0].rpartition('\\')
    tempDir = plv.GENRESPLITPATH+'\\'+shortDst[0]
    dst = tempDir+'\\'+x[2]
    moveFile(src, dst)
    
def cmd_banish(buf):
    for fn in plv.rr:
        banishFile(fn)
    print 'Banished '+str(plv.lenrr)+' files.'

def cmd_rm(buf):
    s = getAlias(buf[0].lower())
    if s not in plv.playlists:
        print 'Tag doesn\'t exist.'
    elif plv.rr == []:
        print 'No files (from search) to modify.'
    else:
        invalidate(s)
        ctr = 0
        for fn in plv.rr:
            if fn in plv.taglists and s in plv.taglists[fn]:
                plv.taglists[fn].remove(s)
                plv.playlists[s].remove(fn)
                if plv.playlists[s] == []:
                    invalidate()
                ctr += 1
        print 'Removed tag from '+str(ctr)+' entries.'
            
def cmd_show(buf):
    if plv.directorySearch:
        print 'Can\'t do this in a directory search.'
        plv.continueFlag = True
        return
    s = getAlias(buf[0].lower())
    if s not in plv.playlists:
        print 'Tag doesn\'t exist.'
    else:
        plv.orderASpecialSearch = True
        plv.rr = plv.playlists[s][:]

def cmd_fwd(buf):
    traverseCmd(buf[0], 1)
    
def cmd_back(buf):
    traverseCmd(buf[0], -1)

def cmd_list(buf):
    print '\t'.join(plv.plkeys)

def cmd_tags(buf):
    ctr = 0
    if plv.rr != []:
        for r in plv.rr:
            ctr += 1
            s = tagsAsString(r)
            print bracketNum(ctr) + s
    else:
        print 'Nothing in selection.'
        
def cmd_wipe(buf):
    wipePlaylists()

def cmd_inv(buf):
    invalidate()
    print 'Invalidated everything.'
    
def cmd_wn(buf):
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
    plv.rr = list(filter(lambda x: '\\+ Albums\\' not in x, plv.rr))
    print 'Non-album songs from less than '+str(n)+' days ago:'
    newr = list(filter(lambda x: fileIsNewAndExists(x, n), plv.rr))
    if newr != []:
        plv.orderASpecialSearch = True
        plv.rr = newr[:]
    else:
        print 'No results. Reverting to last search.'

def cmd_rating(buf):
    parsed = parseCmd(buf[0])
    bl = len(parsed)
    try:
        if bl == 1:
            rrIndex = -1
            n = int(parsed[0])
            pickList = plv.rr
        else:
            rrIndex = int(parsed[0])
            n = int(parsed[1])
            pickList = [plv.rr[rrIndex-1]]
    except:
        print 'Invalid input.'
        return
    for r in pickList:
        key = plv.fileNames2sortKeys[r]
        if key in plv.ratingdata:
            print r+': changed from '+str(plv.ratingdata[key])+' to '+str(n)+'.'
        else:
            print r+': new rating '+str(n)+'.'
        plv.ratingdata[key] = n
        plv.ratingdataChanged = True

def ratings_zero_map(x):
    i = rating(x)
    if i == 0:
        return ''
    else:
        return str(i)

def cmd_ratings(buf):
    printResults(list(map(ratings_zero_map, plv.rr)))

def ageBetween(fn, a, b):
    td = fileAge(fn)
    return td >= a and td <= b

def cmd_time(buf):
    default_time_const = 30
    try:
        inputl = parseCmd(buf[0])
        print inputl
        if len(inputl) == 0:
            a = fileAge(plv.rr[0]).days - default_time_const/2
            b = a + default_time_const
            print 'Defaulting to age of first result file.'
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
    plv.rr = list(filter(lambda x: plv.ALBUMPATH not in x, plv.lines))
    a = datetime.timedelta(days=a)
    b = datetime.timedelta(days=b)
    plv.rr = list(filter(lambda x: ageBetween(x, a, b), plv.rr))
    plv.orderASpecialSearch = True
    addMacro('/p')
    
def fnFilter_nonSet(fn):
    return not fn.startswith(plv.SETPATH)

def cmd_save(buf):
    inputl = parseCmd(buf[0])
    if len(inputl) == 0 or inputl[0].strip() == '':
        print 'Invalid input.'
        return
    dst = opj(plv.SAVEDPLAYLISTPATH, inputl[0])+plv.plExt
    writePls(dst, list(filter(fnFilter_nonSet, plv.rr)), True)
    print 'Saved playlist to: '+dst
    
def fnFilter_ratingOverN(fn, n):
    k = plv.fileNames2sortKeys[fn]
    if k in plv.ratingdata:
        r = plv.ratingdata[k]
    else:
        r = 0
    return r >= n

def cmd_over(buf):
    try:
        n = int(buf[0])
    except ValueError:
        n = 1
    print 'Playing songs with rating >= '+str(n)
    plv.rr = list(filter(lambda x: fnFilter_ratingOverN(x, n), plv.lines))
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
    return list(map(lambda y: y.strip().replace(spaceHolderString, ' '), x.split(' ')))

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
        elif c == '\\':
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

#parsing within-list numerical selections
def parseSelect(s, mini, maxi):
    ranges = list(map(lambda x: x.strip(), s.split(',')))
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
                    ret = list(filter(lambda x: x not in y, ret))
        except:
            print 'Bad selection.'
            ret = []
    return ret

def wipePlaylists():
    l = listdir(plv.ROOTDIR)
    for fn in l:
        if fn.endswith(plv.plExt):
            os.remove(plv.ROOTDIR+fn)
    print 'Wiped playlists.'
    invalidate()

def killTag(t, doInvalidate = True):
    if t in plv.playlists:
        plv.didAnything = True
        if doInvalidate:
            del plv.playlists[t]
            if t in plv.plkeys:
                plv.plkeys.remove(t)
            invalidate()
        else:
            print 'No-invalidate flag set: '+t
        plv.playlists[t] = []
        for r in plv.taglists:
            if t in plv.taglists[r]:
                plv.taglists[r].remove(t)
        print 'Killed tag: '+t
    else:
        print 'Tag doesn\'t exist.'
    
def printResults(res):
    srcCtr = 0
    for r in res:
        try:
            print bracketNum(srcCtr+1)+r
            srcCtr += 1
        except UnicodeEncodeError:
            print '- bad string decode -'
    if srcCtr > 0:
        print ''
    if plv.directorySearch:
        print 'This is an ALBUM search.'
    print 'Found '+str(srcCtr)+' items.'

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
    return lambda x: stringContainsPosNotNeg(x, pos, neg)

def orderSearch(x, res):
    if res != []:
        if x == '':
            filterPN = lambda x: True
        else:
            words, negwords = parseCmd(x, 'pn') #differentiate between positive and negative search terms
            filterPN = filterPosNeg(words, negwords)
        if plv.comesFromDirectorySearch or plv.directorySearch:
            res = list(filter(filterPN, res))
        else:
            res = sorted(list(filter(filterPN, res)), key=rating, reverse=True)
    printResults(res)
    if x != '':
        plv.cmdLog.append(x)
    return res

def rating(fn):
    sk = plv.fileNames2sortKeys[fn]
    try:
        return plv.ratingdata[sk]
    except KeyError:
        return 0
                                                
def grabInput(cq):
    notfirst = True
    if cq == []:
        instr = raw_input('>> ')
        cq += instr.split(';')
        notfirst = False
    x = cq.pop(0).strip()
    if notfirst:
        print '>> '+x
    return x

def main():
    if not os.path.exists(plv.ROOTDIR):
        print plv.ROOTDIR+' doesn\'t exist, aborting.'
        raw_input()
        return
    plv.dirFillLines = dirFillToList()
    for l in plv.dirFillLines:
        plv.lines.append(l[0])
        #use dirfill's filename sort key (index 1)
        plv.fileNames2sortKeys[l[0]] = l[1]
        #use dirfill's creation date if available (index 2)
        if len(l) >= 3:
            plv.fileNames2Dates[l[0]] = invDateTimeStr(l[2])
    plv.sortKeys2fileNames = dict((v,k) for (k,v) in plv.fileNames2sortKeys.items())
    readRatingData()
    fillTagAliases()
    readtags()
    readDirs()
    
    if len(sys.argv) > 1 and sys.argv[1] == '-menu':
        argv = sys.argv[0:1]
        if len(sys.argv) > 2:
            argv += sys.argv[2:]
        menu.main(argv)
        sys.exit(0)
    
    if needAutoBackup():
        print 'Doing autobackup.'
        doBackup(['-doe'])
    else:
        print 'No autobackup needed.'
        
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
        if not isTheCommand(x, 'move'):
            x = x.lower()
        if x in plv.quitlist:
            if x == '/ns':
                plv.saveAtEnd = False
            break
        orderASearch = False
        refinedSearch = False
        plv.orderASpecialSearch = False
        doASelection = False
        plv.continueFlag = False
        if x != '':
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
                orderASearch = True
                refinedSearch = True
        elif x[0] == '/':
            print 'Failed command?'
        else:
            orderASearch = True
        if doASelection:
            if plv.rr != []:
                ps = parseSelect(sele, 1, plv.lenrr)
                if plv.directorySearch and len(ps) == 1:
                    addMacro('/ds;/cfds on;"'+plv.rr[ps[0]]+'";/cfds off')
                    continue
                elif ps != []:
                    plv.orderASpecialSearch = True
                    plv.rr = [plv.rr[i] for i in ps]
                else:
                    print 'No results. Reverting to last search.'
            else:
                print 'Can\'t select from nothing.'
        if plv.orderASpecialSearch:
            orderASearch = True
            refinedSearch = True
            x = ''
        if orderASearch:
            if not refinedSearch:
                if plv.directorySearch:
                    plv.rr = plv.dirlist
                else:
                    plv.rr = plv.lines
            newSearch(orderSearch(x, plv.rr))
            plv.allowRefine = True
    
    if not nothingToDo() and plv.saveAtEnd:
        print '\nWriting tags & playlists...'
        writetags()
    else:
        print '\nNothing was done. No need to save.'
    saveLog()
    print 'Bye!'
    waitAtEnd()
    
if __name__ == '__main__':
    main()
