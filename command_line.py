import  spotipy
from    tokens import *
from    add_lyrics import *
from    spotipy.oauth2 import SpotifyClientCredentials

from    mutagen.easyid3 import EasyID3
from    mutagen.mp3 import MP3
from    mutagen.id3 import ID3, APIC, USLT

import shutil, os, sys, glob, json
import urllib.request
import argparse

songs_not_changed = []
song_paths =        []
lyr_not_found =     []
song_nos =          []
dest_path =         ""

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
    # First have to check if user wants to overwrite over old cover art,
    # if they don't, then it checks if there is already a covert art,
    # if there is one then nothing is added.

    if options.overwrite:
        file = ID3( song_info["mp3_path"] )  # Load mp3
        file.delall("APIC")     # Delete every APIC tag (Cover art)
        file.save()             # Save mp3

        audio_mutagen = MP3(song_info["mp3_path"], ID3=ID3)
        
        audio_mutagen.tags.add( APIC(
            mime='image/jpeg',
            type=3,
            desc=u'Cover',
            data=open( song_info["img_path"] ,'rb').read() )
        )
        
        audio_mutagen.save()

    else:
        # checking if cover already exists, if it does then skip...
        has_pic_or_not = False
        tmp = ID3(song_info["mp3_path"])
        
        for s, t in tmp.items():
            if "APIC" in s:
                print("> Cover art detected, skipping...")
                has_pic_or_not = True
                
                break

        tmp.save() # closing file

        # if no cover is found, then add art...
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
        return 0
    
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

def get_songs(path):
    if not os.path.exists(path):
        return 0
    
    # in case user already adds in the slash in the string
    if path[-1] == "\\" or path[-1] == "/":
        songs_path_str = path + "*.mp3"

    else:
        songs_path_str = path + "\*.mp3"
    
    for mp3 in glob.glob(songs_path_str):
        song_paths.append(mp3)

    return 1

def get_options(args):
    parser = argparse.ArgumentParser(description='Program to add metadata to unorganized MP3s via the Spotipy API.')
    
    parser.add_argument("-u", "--uri",
                        help="URI of specific song on Spotify. If used, \
                                Spotify prompt will not be shown.")
    parser.add_argument("-i", "--input",
                        help="Input MP3 file, used when URI is provided.")
    parser.add_argument("--overwrite", action='store_true',
                        help="This option will delete old info and replace it with new one. \
                                Use it if you want to replace Cover art.")
    parser.add_argument("--add-lyrics", action='store_true',
                        help="Only search for and add lyrics to mp3.")
    
    parser.add_argument("-p", "--path",
                        help="Path to where all songs are stored.")

    options = parser.parse_args(args)

    return options

def add_lyrs_only(song):
    name = os.path.basename( song )
    print()
    print("#"*5 + " Adding lyrics to \"%s\" file "%(name) + "#"*5)

    if not add_lyrics( song ):
        print("\n")

    return 1

def custom_download( uri ):
    raw_song_info = sp.track( uri )
    
    song_info = extract_uri_info( raw_song_info )

    song_info["mp3_path"] = options.input

    return add_metadata(song_info)

def extract_uri_info( results ):
    tmp_dict = {}

    tmp_dict["song_name"] =	    results["name"]
    tmp_dict["arts_names"] =        extract_artists(results["artists"])
    tmp_dict["album_arts"] =        extract_artists(results["album"]["artists"])
    tmp_dict["album"] =             results["album"]["name"]	
    tmp_dict["release_date"]=       results["album"]["release_date"]
    tmp_dict["track_num"] =         results["track_number"]
    tmp_dict["total_tracks"]=       results["album"]["total_tracks"]
    tmp_dict["img_path"] =          download_img( results["album"]["images"][0]["url"] )

    return tmp_dict    

def main():
    try:
        ## Add only lyrics route...
        if options.add_lyrics:
            for song in song_paths:
                add_lyrs_only( song )

        ## URI route...
        elif options.uri is not None:
            # Check if user passed '--path', say to use '-i'
            # instead since if they're using '--path' then
            # all the mp3 are gonna have the same info OR
            # if they haven't used '-i', say to you have to pass it.
            if options.path is not None or options.input is None:
                print("Please use '-i' or '--input' and provive an MP3 file.")
                
                return 0
            
            if custom_download( options.uri ):
                print(">> Info added successfully! <<")
                return 1

            else:
                return 0

        else: 
            for song in song_paths:
                name = os.path.basename( song )
                print()
                print("#"*5 + " Loading \"%s\" file "%(name) + "#"*5)
                song_info = search_song(name)

                if song_info == None:
                    continue

                song_info["mp3_path"] = song
                if add_metadata(song_info):
                    move_song(song_info["mp3_path"], dest_path_str)
            
    except KeyboardInterrupt:
        print("\n> cancelling processes... <")

    show_songs_not_changed()
    show_lyrics_not_found()
    delete_all_imgs()
    
    return 1

if __name__ == '__main__':
    options = get_options( sys.argv[1:] )

    # Create folder within path given so songs that
    # have already been edited can be moved out of the way.
    # in case user already adds in the slash in the string
    # IF '--path' is used instead of '--input'.
    if options.path is not None:
        if not get_songs(options.path):
            print("> Dir does not exist! <")
        
        dest_path_str = options.path
        dest_path_str += "DONE" if dest_path_str[-1] == "\\" or dest_path_str[-1] == "/" else "\\DONE"
    
        if not os.path.exists( dest_path_str ):
            os.makedirs( dest_path_str )    

    client_credentials_manager = SpotifyClientCredentials(client_id=client,
                                                          client_secret=client_sec)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    main()
        
