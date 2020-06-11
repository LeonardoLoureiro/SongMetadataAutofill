import  spotipy
from    tokens import *
from    add_lyrics import *
from    spotipy.oauth2 import SpotifyClientCredentials

from    mutagen.easyid3 import EasyID3
from    mutagen.mp3 import MP3
from    mutagen.id3 import ID3, APIC, USLT

import shutil
import os
import glob
import urllib.request

if not os.path.exists("imgs"):
    print("'imgs' folder not found, creating...")
    os.makedirs("imgs")
    
if not os.path.exists("songs"):
    print("'songs' folder not found, creating...")
    os.makedirs("songs")
    if not os.path.exists("songs/DONE"):
        os.makedirs("songs/DONE")

songs_not_changed = []
song_paths =        []
lyr_not_found =     []
song_nos =          []
dest_path =         "songs/DONE"

def main():
    get_songs()

    try:
        for song in song_paths:
            name = os.path.basename( song )
            print()
            print("#"*5 + " Loading \"%s\" file "%(name) + "#"*5)
            song_info = search_song(name)

            if song_info == None:
                continue

            song_info["mp3_path"] = song
            if add_metadata(song_info):
                move_song(song_info["mp3_path"], dest_path)
            
    except KeyboardInterrupt:
        print("\n> cancelling processes... <")

    show_songs_not_changed()
    show_lyrics_not_found()
    delete_all_imgs()
    
    return 1

# This function should work for all ID3 tag versions...
def add_metadata(song_info):
    print("> Adding info to MP3...")

    audio = EasyID3( song_info["mp3_path"] ) 

    audio["album"] =        song_info["album"]
    audio["title"] =        song_info["song_name"]
    audio["artist"] =       song_info["arts_names"]
    audio["date"] =         song_info["release_date"][0:4]
    audio["albumartist"] =  song_info["album_arts"]

    # Number of album tracks user format "%d/%d".
    audio["tracknumber"] = "%s/%s" % (song_info['track_num'], song_info['total_tracks'] )

    # making sure all tags above are applied to mp3
    audio.save()

    # This complicated little chunk of code is to simply embed the
    # cover art to the mp3. The wrapper (EasyID3) doesn't
    # have the actual item for image, so have to do it manually.
    # First have to check if a cover art already exists in mp3 by
    # checking if 'APIC' tag exists. If it does, adding cover art is skipped.
    
    has_pic_or_not = False
    tmp = ID3(song_info["mp3_path"])

    # check if cover already exists
    for s, t in tmp.items():
        if "APIC" in s:
            print("> Cover art detected, skipping...")
            has_pic_or_not = True
            
            break

    tmp.save()

    # Now adding album cover if none is present...
    if not has_pic_or_not:
        audio_mutagen = MP3(song_info["mp3_path"], ID3=ID3)
        
        audio_mutagen.tags.add( APIC(
            mime='image/jpeg',
            type=3,
            desc=u'Cover',
            data=open( song_info["img_path"] ,'rb').read() )
        )
        
        audio_mutagen.save()

    # adding lyrics, all functions are found in "get_lyrics.py"
    if not add_lyrics( song_info["mp3_path"] ):
        print("\n")
    
    return 1

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

def search_song(name):
    name2 = name[:-4]

    print("\tSearching \"%s\" song..." % (name2) )
    results = sp.search(q=name2, type='track')

    correct_song = choose_corr_song(results)

    # if song isn't found add to list of songs not edited
    if correct_song == None:
        songs_not_changed.append(name)

    return correct_song
    
    
# iterating over all results obtained from search to look for correct one
def choose_corr_song(results):
    try_n = 0
    num_of_results = len(results["tracks"]["items"])

    # asking user if info is correct, keeps going until end of results,
    # default for spotipy is 10.
    for song_result in results["tracks"]["items"]:
        song_info = {}
        song_info = extract_info(results, try_n)
        
        show_song_info(song_info)
        user_i = input("\nCorrect (y/n)?\n> ")
        if user_i == "n" or user_i == "N":
            try_n += 1
            continue                        

        elif user_i == "y" or user_i == "Y":
            # if all if correct, then album cover is downloaded...
            print("> Downloading  and saving album image...")
            song_info["img_path"] = download_img(song_info["image"])

            return song_info

    # making sure if end of results is reached, then user could not
    # find their song, thus adding to list of songs not edited.
    # Also if no song is found on Spotify's end
    # it's also added to this list.
    if try_n == num_of_results:
        print("\n" + "-"*10 + " No more results from search " + "-"*10)
        return None

def show_song_info(song_info):
    print("\nFound song:")
    for i in song_info:
        tmp_str = i
        tmp_str = tmp_str.ljust(25, '.') # pads out string with '.'
        print("\t%s%s" % (tmp_str, song_info[i]) )

# try_n refers  to the position of which search item is the
# one the user wants on the original JSON variable Spotipy returned.
def extract_info(results, try_n):
    tmp_dict = {}

    tmp_dict["song_name"] =	    results["tracks"]["items"][try_n]["name"]
    tmp_dict["arts_names"] =        extract_artists(results["tracks"]["items"][try_n]["artists"])
    tmp_dict["album_arts"] =        extract_artists(results["tracks"]["items"][try_n]["album"]["artists"])
    tmp_dict["album"] =             results["tracks"]["items"][try_n]["album"]["name"]	
    tmp_dict["release_date"]=       results["tracks"]["items"][try_n]["album"]["release_date"]
    tmp_dict["track_num"] =         results["tracks"]["items"][try_n]["track_number"]
    tmp_dict["total_tracks"]=       results["tracks"]["items"][try_n]["album"]["total_tracks"]   
    tmp_dict["image"] =             results["tracks"]["items"][try_n]["album"]["images"][0]["url"]

    return tmp_dict

# function for songs that have multiple artists.
# Mutgen can add multiple artists to an mp3 and
# accepts it as a list. HOWEVER, iTunes doesn't
# register all of them, just the first but and
# when it does it shows them all separated by a '/'.
def extract_artists(results_artists):
    arts_list = []
    art_name = ""

    for artist in results_artists:
        arts_list.append(artist["name"])

    return arts_list

# downloads album art to folder 'imgs'
def download_img(url):
    img_name = os.path.basename(url)
    img_path = "imgs\\" + img_name + ".jpg"

    urllib.request.urlretrieve(url, img_path)

    return img_path

# function to remove all cover photos,
# if you want to keep them just comment function
# on main().
def delete_all_imgs():
    print("\n> cleaning up imgs dir... <")
    for img in glob.glob('imgs\*.jp*g'):
        os.remove(img)

    print("> clean up complete! <")
        
def move_song(song_path, dest_path):
    new_dest = shutil.move(song_path, dest_path)
    print("> Successfully moved song: %s" % (os.path.basename(new_dest)) )

def show_songs_not_changed():
    # if everything ran ok, then don't bother printing list
    if not songs_not_changed:
        return

    print("="*30 + " MP3s not edited: " + "="*30)

    for mp3 in songs_not_changed:
        print("> %s" % mp3)

def get_songs():
    for mp3 in glob.glob("songs\*.mp3"):
        song_paths.append(mp3)

# just usual authentication stuff...
if __name__ == '__main__':
    client_credentials_manager = SpotifyClientCredentials(client_id=client, client_secret=client_sec)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    main()

# To see all possible tags that EasyID3 can add to mp3s, just run:
#  print( EasyID3.valid_keys.keys() )
