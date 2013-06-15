cd ~/pystuff/playlistmaker
./adhoc_rename.py
./movestuff.py $@
./dirfill.py -a
echo "/new;/automp;//" > $PLAYLISTMAKER_DIR/data/preprocess.txt
./playlistmaker.py
rm $PLAYLISTMAKER_DIR/data/preprocess.txt