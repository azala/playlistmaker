#!/usr/bin/env python

import os
from azutils import *

#constants
plExt = '.m3u8'
cSep = '/'
cEncoding = 'NFC'

PLMAKERDIR = os.path.expanduser('~/pystuff/playlistmaker')
CDATAPATH = opj(PLMAKERDIR,'data')
ROOTDIR = '/Volumes/IPOD'

GENRESPLITPATH = opj(ROOTDIR, '+ Genre Split')
NEWESTPATH = opj(GENRESPLITPATH, '+ NEWEST')
REALLYNEWESTPATH = opj(GENRESPLITPATH, '+ REALLY NEWEST')
ALBUMPATH = opj(GENRESPLITPATH, '+ Albums')
DONTWANTPATH = opj(GENRESPLITPATH, 'z(don\'t want, duplicates or crap)')
LASTPLSPATH = opj(CDATAPATH, 'last')+'.m3u'
IPODBACKUPDIR = opj(ROOTDIR, 'backups')
EXPORTDIR = opj(IPODBACKUPDIR, 'export')
BACKUPDIRS = [CDATAPATH, IPODBACKUPDIR]
SAVEDPLAYLISTPATH = opj(ROOTDIR, 'saved playlists')
SETPATH = opj(GENRESPLITPATH, '+ sets')
MOVEDPATH = opj(ROOTDIR, 'moved')
DESKTOP = os.path.expanduser('~/Desktop')
LOCALSONGSPATH = opj(DESKTOP,'+ MUSIC')
MOVESTUFFDIRS = [DESKTOP,
                 os.path.expanduser('~/Downloads')];

lock_file = opj(CDATAPATH, 'lock')
preprocess_file = opj(CDATAPATH, 'preprocess.txt')
tagfile = opj(CDATAPATH, 'tags.txt')
DIRFILLPATH = opj(CDATAPATH, 'dirfill.txt')
tag_indexfile = opj(CDATAPATH, 'tag_index.txt')
tag_priorityfile = opj(CDATAPATH, 'priority_tag_index.txt')
tag_aliasfile = opj(CDATAPATH, 'tag_aliases.txt')
albumfile = opj(CDATAPATH, 'albums.txt')
cmdLogFile = opj(CDATAPATH, 'searchlog.txt')
cmdListFile = opj(CDATAPATH, 'commandlist.txt')
ratingFile = opj(CDATAPATH, 'ratings.txt')
localDirfillFile = opj(CDATAPATH, 'local-dirfill.txt')
historyFile = opj(CDATAPATH, 'command-history.txt')

VLCSOCK = '~/vlc.sock' #rc interface socket
#mediaplayer = 'winamp'
#mediaplayer = '/Applications/VLC.app/Contents/MacOS/VLC '
vlc = 'open -a vlc.app'
vlc_rc = '/Applications/VLC.app/Contents/MacOS/VLC --rc-unix '+VLCSOCK+' --rc-fake-tty'# > /dev/null &'
#second_mediaplayer = 'open -a itunes.app'
second_mediaplayer = 'open -a cog.app'
redirect_stderr = '2> /dev/null'

#notepad = 'notepad++'
notepad = 'open -e'
extns = ['mp3','wav','aac','ogg','flac','wma','m4a','mid']
excludedirs = [opj(ROOTDIR, '.Trashes'),
               DONTWANTPATH,
               opj(GENRESPLITPATH, 'other'),
               opj(ROOTDIR, '.rockbox'),
               MOVEDPATH,
               IPODBACKUPDIR]
no_lowercase_conversion_commands = ['move','sys','msg','art']
FUNC_PREFIX = 'cmd_'
AUTOBACKUP_INTERVAL = 3 #days after last backup before automatically making another
VLCSOCK_DELAY = 0.2 #sleep time between the call to open vlc and the call to play
TRIVIAL_TAGS = ['non-album', 'most popular', 'not as popular', 'concentration']

#messages
cBadStr = '- bad string decode -'
cZeroTime = time.gmtime(0)
cIpodMissing = 'iPod missing ('+ROOTDIR+').'

#settings
WAITATEND = False
NOIPODMODE = False
USE_VLC_RC = False #use remote control interface
if USE_VLC_RC:
    mediaplayer = vlc_rc
else:
    mediaplayer = vlc
AUTO_EXPORT = False

#variables
#orphans = []
#playlists = {} #values are full file names
#taglists = {} #keys are full file names
#plkeys = []
quitlist = ['//', '/quit', '/exit', '/ns']
helplist = ['?', '/h', '/help']
lastTag = None
results = []
cmdQueue = []
ptag_index = []
songs = []
songDict = {'fn':{},
            'sk':{},}
tags = []
#tagsByName = {}
tagCompletionList = [] #basically all the tagnames
cmdCompletionList = []
#tag_aliases = {}
fileNames2sortKeys = {}
sortKeys2fileNames = {}
tagToPlaylist = {} #tag name -> its associated playlist name
#keys are full file names
#values are struct_time
fileNames2Dates = {}
saveAtEnd = True
#move_file_queue = []
dirFillLines = []
needRewriteDirfill = False
invalidateTheseTags = []
invalidateAllTags = False
dirlist = []
cmdLog = []
commandlist = []
#key = sortkey
#value = rating
ratingdata = {}
ratingdataChanged = False
lines = []
resultHistory = []
resultHistory_DSFlag = []
resultHistoryTerms = []
#resultHistory_NoSortFlag = []
rptr = -1
maxStoredResults = 100
rr = []
lastCmdWasSearch = False
didAnything = False
directorySearch = False
comesFromDirectorySearch = False
continueFlag = False
allowRefine = False
orSearch = False
orderASearch = False
refinedSearch = False
#nosort = False
lenrr = 0
orderASpecialSearch = False
needToCallDirfill = False
aliasesChanged = False
itunes_flag = False
cur_autotag_index = -1
autotag_saved_search = []
INITIALIZED = True
MENU_AVAILABLE = False
