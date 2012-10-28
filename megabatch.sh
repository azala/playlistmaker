cd ~/pystuff/playlistmaker
./adhoc_rename.py
./movestuff.py $@
./dirfill.py -a
echo "/new;//" > $PLAYLISTMAKER_DIR/data/preprocess.txt
./playlistmaker.py