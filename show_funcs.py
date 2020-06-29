def show_song_info(song_info):
    print("\nFound song:")
    for i in song_info:
        tmp_str = i
        tmp_str = tmp_str.ljust(25, '.') # pads out string with '.'
        print("\t%s%s" % (tmp_str, song_info[i]) )

def show_songs_not_changed():
    # if everything ran ok, then don't bother printing list
    if not songs_not_changed:
        return

    print("="*30 + " MP3s not edited: " + "="*30)

    for mp3 in songs_not_changed:
        print("> %s" % mp3)

def show_lyrics_not_found():
    if not lyr_not_found or not song_nos:
        return 0
    
    print("~"*40)
    
    print(">> Song lyrics not found: <<")
    for song in lyr_not_found:
        print("> %s" % song)

    print("*"*40)

    print(">> Songs said no to: <<")
    for song in song_nos:
        print("> %s" % song)

    print("~"*40)
