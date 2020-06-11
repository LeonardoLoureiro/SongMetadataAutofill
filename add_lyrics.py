import glob
import urllib.request
import requests
from bs4 import BeautifulSoup as soup

from    mutagen.easyid3 import EasyID3
from    mutagen.mp3 import MP3
from    mutagen.id3 import ID3, USLT

import os
import sys

base_search_url = "https://search.azlyrics.com/search.php?q="
name_list = []

def add_lyrics(song_path):

    song_name = get_song_info(song_path)

    req_url = base_search_url + song_name

    lyr_page = get_lyr_page(req_url)
    if lyr_page == None:
        return 0

    lyrics = extract_lyrics(lyr_page)

    add_lyrics_to_mp3(song_path, lyrics)

    return 1
    
def get_song_info(song_path):
    title_and_artists = ""

    audio = EasyID3(song_path)

    # info comes in list form
    buffer = audio["title"] + audio["artist"]
    title_and_artists = " ".join(buffer)
    title_and_artists = title_and_artists.replace('(', '')
    title_and_artists = title_and_artists.replace(')', '')

    audio.save()
    
    return title_and_artists


def add_lyrics_to_mp3(song_path, lyrics):
    mp3 = MP3(song_path, ID3=ID3)

    mp3.tags.add( USLT(
        encoding=3,
        lang=u'eng',
        desc=u'desc',
        text=lyrics
    ))
    
    mp3.save()

    print(">> Lyrics added to mp3! <<\n")

    return 0

def get_lyr_page(req_url):
    resp = requests.get(req_url)
    html = soup(resp.text, features="html.parser")

    match = html.find_all("td", class_="text-left visitedlyr")

    # If AZLyrics doesn't have lyrics to this song...
    if not match:
        print("> Song not found!")
        return None

    lyr_page_url = choose_lyr(match)

    if lyr_page_url == None:
        print("> No lyrics chosen, skiping lyrics...")
        return None

    return lyr_page_url

# "list_of_lyrs" type if already in "soup" class,
# so no need to pass it through "soup()" function
def choose_lyr(list_of_lyrs):
    found = False
    print()
    
    for search_block in list_of_lyrs:
        lyr_sample = search_block.find("small")
        lyr_sample = lyr_sample.get_text()
        
        print("-"*40)
        print("Lyric sample:")
        print("> {}".format(lyr_sample))
        print("\nAre lyrics correct?")
        correct_or_not = input("> ")

        if correct_or_not == 'y':
            lyr_url = search_block.find("a")['href']

            return lyr_url

        elif correct_or_not == 'n':
            continue

    if found == False:
        return None

def extract_lyrics(lyr_page):
    lyrics_page_raw = urllib.request.urlopen(lyr_page).read()
    lyrics_page_soup = soup(lyrics_page_raw, features="html.parser")
    
    lyrics_block = lyrics_page_soup.find("div", class_="col-xs-12 col-lg-8 text-center")

    # the div which has all lyrics doesn't have
    # class or id, so have to choose by it's position.
    lyr_raw = lyrics_block.find_all("div")[5]

    # scrubbing html texts like <div> or <br/>
    lyr_clean = lyr_raw.get_text()
    
    return lyr_clean

if __name__ == '__main__':
    get_lyr_page("https://search.azlyrics.com/search.php?q=marry+the+night")
