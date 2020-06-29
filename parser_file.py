import argparse

def get_options(args):
    MainParser = argparse.ArgumentParser(description='Program to add metadata to unorganized \
                                                    MP3s via the Spotipy API.')
    
    MainParser.add_argument("-u", "--uri", metavar=('\"spotify:track:VALUE\"'),
                                help="URI of specific song on Spotify. If used, \
                                Spotify prompt will not be shown.")
    
    MainParser.add_argument("--overwrite", action='store_true',
                                help="This option will delete old info and replace it with new one. \
                                Use it if you want to replace Cover art.")
    MainParser.add_argument("--add-lyrics", action='store_true',
                                help="Only search for and add lyrics to mp3.")
    MainParser.add_argument("-k", "--keep-imgs", action='store_true',
                                help="Keep all cover arts downloaded.")
    MainParser.add_argument("-e", "--explicit", action='store_true',
                                help="Add explicit tag to song(s). Can be used as stand-alone \
                                or in conjuction with '-p'.")
    
    MainParser.add_argument("-n", "--no-moving", action='store_true',
                                help="Stops program from moving song file after it's done with it, file remains in \
                                the same dir.")

    # The basics of this chunk of code is to force user to choose one,
    # since each can only be used for some scenarios while another
    # might not be the best choice.
    # '-i' is best for '-u'
    # '--list-file' can be replaced with '-p'
    # and vice versa.
    get_songs = MainParser.add_mutually_exclusive_group(required=True)

    get_songs.add_argument("--list-file", metavar=('FILE.txt'),
                                help="Instead of using '-p' or '-i' to list all files you want to edit, \
                                you can add paths to specific songs as a list to a text file. One per line.")
    get_songs.add_argument("-i", "--input", metavar=('FILE.mp3'),
                                help="Input MP3 file, used when URI is provided.")
    get_songs.add_argument("-p", "--path",
                                help="Path to folder where all songs are stored.")

    options = MainParser.parse_args(args)

    return options
