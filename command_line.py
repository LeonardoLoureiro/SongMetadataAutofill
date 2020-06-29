import  spotipy
from    spotipy.oauth2 import SpotifyClientCredentials

from    tokens import *
from    show_funcs import *
from    add_lyrics import *
from    parser_file import get_options

from    mutagen.easyid3 import EasyID3
from    mutagen.easymp4 import EasyMP4

from    mutagen.mp4 import MP4, MP4Cover
from    mutagen.id3 import ID3, APIC

import shutil, os, sys, glob
import urllib.request

songs_not_changed = []

song_paths =        []
song_paths_itunes = []

lyr_not_found =     []

song_nos =          []
dest_path =         ""

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

# try_n refers to the position of which search item is the
# one the user wants in the original JSON variable Spotipy returned.
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
    tmp_dict["explicit"] =          results["tracks"]["items"][try_n]["explicit"]

    return tmp_dict

# function for songs that have multiple artists.
# Mutgen can add multiple artists to an mp3 and
# accepts it as a list.
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
# if you want to keep them just use '-k' option.
def delete_all_imgs():
    print("\n> cleaning up imgs dir... <")
    for img in glob.glob('imgs\*.jp*g'):
        os.remove(img)

    print("> clean up complete! <")
        
def move_song(song_path, dest_path):
    new_dest = shutil.move(song_path, dest_path)
    print("> Successfully moved song: %s" % (os.path.basename(new_dest)) )



def get_songs(path):
    if not os.path.exists(path):
        return 0
    
    # in case user already adds in the slash in the string
    if path[-1] == "\\" or path[-1] == "/":
        songs_path_str = path + "*.mp3"

    else:
        songs_path_str = path + "\*.mp3"

    # for iTune's '.m4a' files.
    if path[-1] == "\\" or path[-1] == "/":
        songs_path_str = path + "*.m4a"

    else:
        songs_path_str = path + "\*.m4a"
    
    for mp4 in glob.glob(songs_path_str):
        song_paths_itunes.append(mp4)

    return 1

def add_lyrs_only(song):
    name = os.path.basename( song )
    print()
    print("#"*5 + " Adding lyrics to \"%s\" file "%(name) + "#"*5)

    if not add_lyrics( song ):
        print("\n")

    return 1

def custom_download_mp3( uri ):
    raw_song_info = sp.track( uri )
    
    song_info = extract_uri_info( raw_song_info )

    song_info["mp3_path"] = options.input

    return add_metadata_mp3(song_info)

def custom_download_m4a( uri ):
    raw_song_info = sp.track( uri )
    
    song_info = extract_uri_info( raw_song_info )

    song_info["mp3_path"] = options.input

    return add_metadata_m4a(song_info)

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
    tmp_dict["explicit"] =          results["explicit"]
                                            
    return tmp_dict

# This function should work for all ID3 tag versions...
def add_metadata_mp3(song_info):
    print("> Adding info to MP3...")

    audio = EasyID3( song_info["mp3_path"] ) 

    audio["album"] =        song_info["album"]
    audio["title"] =        song_info["song_name"]
    audio["artist"] =       song_info["arts_names"]
    audio["date"] =         song_info["release_date"][0:4]
    audio["albumartist"] =  song_info["album_arts"]

    # Number of album tracks user format "%d/%d".
    audio["tracknumber"] = "%s/%s" % (song_info['track_num'], song_info['total_tracks'] )
    audio.save()

    # This complicated little chunk of code is to simply embed the
    # cover art to the mp3. The wrapper (EasyID3) doesn't
    # have the actual item for image, so have to do it manually.
    # First have to check if user wants to overwrite over old cover art,
    # if they don't, then it checks if there is already a covert art,
    # if there is one then nothing is added. If user wants to overwrite,
    # then all 'APIC' tags are deleted and new one is added.

    if options.overwrite:
        song = ID3( song_info["mp3_path"] )  # Load mp3
        song.delall("APIC")     # Delete every APIC tag (Cover art)

        song.add( APIC(
            encoding=0,
            mime='image/jpeg',
            type=3,     # type 3 just means it's the cover of the song
            desc=u'Cover',
            data=open( song_info["img_path"] ,'rb').read() )
        )
        
        song.save()

    else:
        # checking if cover already exists, if it does then skip...
        has_pic_or_not = False
        tmp = ID3( song_info["mp3_path"] )
        
        for s, t in tmp.items():
            if "APIC" in s:
                print("> Cover art detected, skipping...")
                has_pic_or_not = True
                
                break

        tmp.save() # closing file

        # if no cover is found, then add art...
        if not has_pic_or_not:
            song = ID3( song_info["mp3_path"] )
            song.add( APIC(
                encoding=0,
                mime='image/jpeg',
                type=3,
                desc=u'Cover',
                data=open( song_info["img_path"] ,'rb').read()
                )
            )
            
            song.save()

    # adding lyrics, all functions are found in "get_lyrics.py"
    if not add_lyrics( song_info["mp3_path"] ):
        print("\n")
        
        return 0
    
    return 1

def add_metadata_m4a( song_info ):
    # instead of just using basic 'MP4' for ALL tags
    # use both as EasyMP4 handles the most common tags
    # and it's easier to use if, in future, decide to add more info.
    itunes_song = EasyMP4( song_info["mp3_path"] )
    
    itunes_song["album"] =        song_info["album"]
    itunes_song["title"] =        song_info["song_name"]
    itunes_song["artist"] =       song_info["arts_names"]
    itunes_song["date"] =         song_info["release_date"][0:4]
    itunes_song["albumartist"] =  song_info["album_arts"]
    itunes_song["tracknumber"] = "%s/%s" % (song_info['track_num'], song_info['total_tracks'] )

    itunes_song.save()

    # adding tags which are not avaiable through EasyMP4
    img_data = open( song_info["img_path"] ,'rb').read()
    itunes_song = MP4( song_info["mp3_path"] )
    itunes_song.tags["covr"] = [( MP4Cover( img_data ) )] # album art

    itunes_song.tags["rtng"] = [song_info["explicit"]] # rating
    
    itunes_song.save()

    return 1

def make_song_explicit( song_path ):
    if song_path[-4:] != ".m4a":
        print(">> Only M4A files accepted <<")
        return 0
    
    song = MP4( song_path )

    song.tags["rtng"] = [True]

    song.save()

    return 1

def get_songs_from_file( file_path ):
    with open( file_path, 'r', encoding='utf-8' ) as f:
        for line in f.read().splitlines():
            if line[-4:] == ".m4a":
                song_paths_itunes.append( line )

            elif line[-4:] == ".mp3":
                song_paths.append( line )

    return 1

def check_path( path_name ):
    if not os.path.exists( path_name ):
        print(">> Path/File does not exist! <<")
        return 0

    else:
        return 1

def path_init():
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

    elif options.list_file is not None:
        if get_songs_from_file( options.list_file ):
            print(">> Imported list of songs from file... <<")

        else:
            return 0

    elif options.input is not None:
        if check_path( options.input ):
            song_paths_itunes.append( options.input )

    return 1

def main():
    try:
        ## Add lyrics only route...
        if options.add_lyrics:
            for song in song_paths:
                add_lyrs_only( song )

        ## URI route...
        elif options.uri is not None:
            if options.input is None:
                print(">> '-i' is needed for '--uri/-u' option! <<")
                return 0
            
            for song in song_paths:
                custom_download_mp3( options.uri )
                print(">> Info added successfully! <<")
                
                return 1

            for song in song_paths_itunes:
                custom_download_mp3( options.uri )
                print(">> Info added successfully! <<")
                
                return 1

            else:
                return 0

        ## Add explicit tag only route
        # only '.m4a' files are accepted - paths in 'song_paths_itunes'
        elif options.explicit:            
            for song in song_paths_itunes:
                make_song_explicit( song )
                song_name = os.path.basename( song )
                print(">> File %s is now tagged explicit. <<" % song_name)

            print("\n> Rating 'explicit' has been added to song(s) <")

            return 1

        ## Normal route - only '-p' is given.
        else: 
            for song in song_paths:
                name = os.path.basename( song )
                print()
                print("#"*5 + " Loading \"%s\" file "%(name) + "#"*5)
                song_info = search_song(name)

                if song_info == None:
                    continue

                song_info["mp3_path"] = song
                if add_metadata_mp3(song_info):
                    if options.no_moving is False:
                        move_song(song_info["mp3_path"], dest_path_str)

            # in case there's iTunes song files too...
            for song in song_paths_itunes:
                name = os.path.basename( song )
                print()
                print("#"*5 + " Loading \"%s\" file "%(name) + "#"*5)
                song_info = search_song(name)

                if song_info == None:
                    continue

                song_info["mp3_path"] = song
                
                if add_metadata_m4a( song_info ):
                    if options.no_moving is False:
                        move_song(song_info["mp3_path"], dest_path_str)
                        
                    
    except KeyboardInterrupt:
        print("\n> cancelling processes... <")

    show_songs_not_changed()
    show_lyrics_not_found()

    if not options.keep_imgs:
        delete_all_imgs()
    
    return 1

if __name__ == '__main__':
    options = get_options( sys.argv[1:] )
    path_init()

    client_credentials_manager = SpotifyClientCredentials(client_id=client,
                                                          client_secret=client_sec)
    
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    main()        
