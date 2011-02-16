import os

DESKTOP = 'C:\\Documents and Settings\\Michel DSa\\Desktop\\'
EMUSIC = 'E:\\+ Genre Split\\+ NEWEST\\'
ALREADYONIPOD = 'C:\\Documents and Settings\\Michel DSa\\Desktop\\+ ALREADY ON IPOD\\'
#l = list(filter(lambda x: x.endswith('.mp3'), os.listdir(DESKTOP)))
#for fn in l:
if os.path.exists(EMUSIC):
    os.system('copy "'+DESKTOP+'*.mp3" "'+EMUSIC+'" /y')
    os.system('move "'+DESKTOP+'*.mp3" "'+ALREADYONIPOD+'"')
else:
    print 'Not found: '+EMUSIC
#print('Finished: '+fn)
