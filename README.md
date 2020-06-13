# SongMetadataAutofill
Small Python program using various libraries to search for a song online and fill in correct metadata (e.g. album name, artists' names, etc.).

## Before using script
- Create tokens to use the Spotify API, both secret and public. Save them to `tokens.py`.
- `pip install` both `spotipy` and `mutagen`.
- Make sure all MP3s are named as following: `ARTISTS_NAME - NAME_OF_SONG.mp3`. This makes it easier to search for results on Spotify. Move them to the `songs` on the same `dir` as the script.

## How to run
Simply run the script on `terminal` or `cmd` as `py main.py`.
Script will iterate over .mp3s in `songs` folder, then run through each search item Spotify gives you, choose correct one. It will do this to all `.mp3`s, it will download all albums covers too. If you want to keep the `.jpg`s then comment the `delete_all_imgs()` function on `main()`.

## Notes

### Function found in `command_line.py`

| Function	| Arguments     | Returns 	| Calls any other functions? |
| ------------- |:-------------:| :------------:|-------------:|
| `add_metadata`          | dictionary contaning info of song, path to mp3 is included in the dict. | If function if executed correctly then it returns `1`. Otherwise `0`. | `add_lyrics` - found in `add_lyrics.py` |
| `show_lyrics_not_found` | None. Variables used are 'global' within `.py` file.      |   Does not return anything. | None |
| `search_song`       	  | String - basename of `.mp3` name.      | Dict of correct song info. | `choose_corr_song` |
| `choose_corr_song`      | JSON result from Spotipy API.      | Song info extacted from JSON result of Spotipy API. If no result found/not result wanted, then `None`.  | `extract_info`, `show_song_info`, `download_img` |
| `show_song_info`        | Dict of song info.      | None.   | None. |
| `extract_info`          | JSON result from Spotipy API and which of the results is the one desired. | Dict of relevant info from JSON result.   | `extract_artists` |
| `extract_artists`       | Specific dict part of artists derived from JSON response. | List of all artists from the dict passed.   | None. |
| `download_img`          | URL of `.jpg` file given by JSON reponse.      | Path of where `.jpg` is stored in local `dir`. | None |
| `delete_all_imgs`       | None.      | None.   | None. |
| `move_song`             | None.      | None.   | None. |
| `show_songs_not_changed`| None.      | `None` if `songs_not_changed` is empty, otherwise does not return anything.  | None. |
| `get_songs`             | String of path where all `.mp3`s are stored. | `0` is dir does not exist, otherwise does not return anything.   | None. |
| `get_options`           | String of all arguments passed to `main.py` file. | `class` containing all arguments used and their corresponding input values/flag raised.   | None. |