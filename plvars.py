from azutils import *

#constants
plExt = '.m3u8'

CDATAPATH = 'C:\\playlistmaker_data'
ROOTDIR = 'E:\\'

GENRESPLITPATH = opj(ROOTDIR, '+ Genre Split')
NEWESTPATH = opj(GENRESPLITPATH, '+ NEWEST')
ALBUMPATH = opj(GENRESPLITPATH, '+ Albums')
DONTWANTPATH = opj(GENRESPLITPATH, 'z(don\'t want, duplicates or crap)')
LASTPLSPATH = opj(CDATAPATH, 'last')+plExt
BACKUPDIRS = [CDATAPATH, opj(ROOTDIR, 'backups')]
SAVEDPLAYLISTPATH = opj(ROOTDIR, 'saved playlists')

tagfile = opj(CDATAPATH, 'tags.txt')
DIRFILLPATH = opj(CDATAPATH, 'dirfill.txt')
tag_indexfile = opj(CDATAPATH, 'tag_index.txt')
tag_priorityfile = opj(CDATAPATH, 'priority_tag_index.txt')
tag_aliasfile = opj(CDATAPATH, 'tag_aliases.txt')
albumfile = opj(CDATAPATH, 'albums.txt')
cmdLogFile = opj(CDATAPATH, 'searchlog.txt')
cmdListFile = opj(CDATAPATH, 'commandlist.txt')
ratingFile = opj(CDATAPATH, 'ratings.txt')

mediaplayer = 'winamp'
notepad = 'notepad++'
extns = ['mp3','wav','aac','ogg','flac','wma']
excludedirs = [DONTWANTPATH,
               opj(GENRESPLITPATH, 'other'),
               opj(ROOTDIR, '.rockbox'),
               opj(ROOTDIR, 'moved'),
               opj(ROOTDIR, 'backups')]

FUNC_PREFIX = 'cmd_'
AUTOBACKUP_INTERVAL = 3 #days after last backup before automatically making another

#settings
WAITATEND = False

#variables
orphans = []
playlists = {} #values are full file names
taglists = {} #keys are full file names
plkeys = []
quitlist = ['//', '/q', '/quit', '/exit', '/ns']
helplist = ['?', '/h', '/help']
lastTag = None
results = []
cmdQueue = []
ptag_index = []
tag_aliases = {}
fileNames2sortKeys = {}
sortKeys2fileNames = {}
#keys are full file names
#values are struct_time
fileNames2Dates = {}
saveAtEnd = True
move_file_queue = []
dirFillLines = []
needRewriteDirfill = False
invalidateTheseTags = []
invalidateAllTags = False
dirlist = []
cmdLog = []
commandlist = []
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
continueFlag = False
#nosort = False
lenrr = 0
orderASpecialSearch = False

INITIALIZED = True
