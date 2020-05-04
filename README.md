# SongMetadataAutofill
Small Python program using various libraries to search for a song online and fill in correct metadata (e.g. album name, artists' names, etc.).

## Before using script
- Create tokens to use the Spotify API, both secret and public. Save them to `tokens.py`.
- `pip install` both `spotipy` and `mutagen`.
- Make sure all MP3s are named as following: `ARTISTS_NAME - NAME_OF_SONG.mp3`. This makes it easier to search for results on Spotify. Move them to the `songs` on the same `dir` as the script.

## How to run
Simply run the script on `terminal` or `cmd` as `py main.py`.
Script will run throuhg each search item Spotify gives you, choose correct one. It will do this to all `.mp3`s, it will download all albums covers too. If you want to keep the `.jpg`s then comment the `delete_all_imgs()` function on `main()`.