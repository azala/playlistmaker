#!/usr/bin/env python

import os
from azutils import *

#constants
plExt = '.m3u8'
cSep = '/'
cEncoding = 'NFC'

PLMAKERDIR = os.path.expanduser('~/pystuff/playlistmaker')
CDATAPATH = opj(PLMAKERDIR,'playlistmaker_data')
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

#mediaplayer = 'winamp'
#mediaplayer = '/Applications/VLC.app/Contents/MacOS/VLC '

mediaplayer = 'open -a vlc.app'
#second_mediaplayer = 'open -a itunes.app'
second_mediaplayer = 'open -a cog.app'
redirect_stderr = '2> /dev/null'

#notepad = 'notepad++'
notepad = 'open -e'
extns = ['mp3','wav','aac','ogg','flac','wma','m4a']
excludedirs = [opj(ROOTDIR, '.Trashes'),
               DONTWANTPATH,
               opj(GENRESPLITPATH, 'other'),
               opj(ROOTDIR, '.rockbox'),
               MOVEDPATH,
               IPODBACKUPDIR]

FUNC_PREFIX = 'cmd_'
AUTOBACKUP_INTERVAL = 3 #days after last backup before automatically making another

#messages
cBadStr = '- bad string decode -'
cZeroTime = time.gmtime(0)

#settings
WAITATEND = False
NOIPODMODE = False

#variables
#orphans = []
#playlists = {} #values are full file names
#taglists = {} #keys are full file names
#plkeys = []
quitlist = ['//', '/q', '/quit', '/exit', '/ns']
helplist = ['?', '/h', '/help']
lastTag = None
results = []
cmdQueue = []
ptag_index = []
songs = []
songDict = {'fn':{},
            'sk':{},}
tags = []
tagsByName = {}
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
#nosort = False
lenrr = 0
orderASpecialSearch = False
needToCallDirfill = False
aliasesChanged = False
itunes_flag = False

INITIALIZED = True
MENU_AVAILABLE = False
