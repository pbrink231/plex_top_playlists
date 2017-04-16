#!/usr/bin/python

# a python test script
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
#
#         Automated Ranked Playlists - RugbyHunter231
#
#                         *** Use at your own risk! ***
#   *** I am not responsible for damages to your Plex server or libraries. ***
#
#------------------------------------------------------------------------------

import json
import os
import requests
import subprocess
import time
import xmltodict
from lxml.html import parse
from plexapi.server import PlexServer
from plexapi.utils import NA

from urllib2 import Request, urlopen

### Plex server details ###
PLEX_URL = 'http://localhost:32400'
PLEX_TOKEN = '' # This is required.  Check github instructions how to find it

### Trakt API Info ###
TRAKT_API_KEY = '' # This is required.  Please check readme from github [https://github.com/pbrink231/plex_top_playlists]

# Share playlist with other user?
SYNC_WITH_SHARED_USERS = False # Choices True, False -- Caps matter, (if True, syncs all or list, if false, only token user)
ALLOW_SYNCED_USERS = [] # (keep blank for all users, comma list for specific users.) EX ['username','anotheruser'], SYNC_WITH_SHARED_USERS must be True.

### Current library info ###
MOVIE_LIBRARY_NAME = 'Movies'
SHOW_LIBRARY_NAME = 'Shows'

### Trakt Movie Playlist info ###
TRAKT_NUM_MOVIES = 80 # max is 100
TRAKT_WEEKLY_PLAYLIST_NAME = 'Movies Top Weekly'
TRAKT_POPULAR_PLAYLIST_NAME = 'Movies Popular'

### Trakt Show Playlist info ###
TRAKT_NUM_SHOWS = 30 # max is ?
TRAKT_WEEKLY_SHOW_PLAYLIST_NAME = 'Show Top Weekly'
TRAKT_POPULAR_SHOW_PLAYLIST_NAME = 'Show Popular'

### New IMDB Top 250 library details ###
IMDB_CHART_URL = 'http://www.imdb.com/chart/top'
IMDB_PLAYLIST_NAME = 'Movies All Time'


####### CODE HERE (Nothing to change) ############

def get_user_tokens(server_id):
    headers = {'Accept': 'application/json', 'X-Plex-Token': PLEX_TOKEN}
    result = requests.get('https://plex.tv/api/servers/{server_id}/shared_servers?X-Plex-Token={token}'.format(server_id=server_id, token=PLEX_TOKEN), headers=headers)
    xmlData = xmltodict.parse(result.content)
    users = {user['@username']: user['@accessToken'] for user in xmlData['MediaContainer']['SharedServer']}

    return users

def create_playlists(plex, list, playlist_name):
    # Remove old playlists
    #print('{}: Checking if playlist exist to delete if needed'.format(playlist_name))
    for playlist in plex.playlists():
        if playlist.title == playlist_name:
            try:
                playlist.delete()
                #print("{}: Playlist deleted".format(playlist_name))
            except:
                print("ERROR - cannot delete playlist: {}".format(playlist_name))
                return None

    plex.createPlaylist(playlist_name, list)
    #print("{}: playlist created".format(playlist_name))

def loop_plex_users(plex, list, playlist_name):
    #update my list
    create_playlists(plex, list, playlist_name)

    #update list for shared users
    if SYNC_WITH_SHARED_USERS:
        plex_users = get_user_tokens(plex.machineIdentifier)
        for user in plex_users:
            if not ALLOW_SYNCED_USERS or user in ALLOW_SYNCED_USERS:
                print("{}: updating playlist for user {}".format(playlist_name, user))
                user_token = plex_users[user]
                user_plex = PlexServer(PLEX_URL, user_token)
                create_playlists(user_plex, list, playlist_name)


def setup_show_playlist(plex, tvdb_ids, plex_shows, playlist_name):
    if tvdb_ids:
        # Create a list of matching shows using last episode
        print("{}: finding matching movies for playlist with count {}".format(playlist_name, len(tvdb_ids)))
        matching_episodes = []
        sorted_shows = []
        for show in plex_shows:
            last_episode = show.episodes()[-1]
            if last_episode.guid != NA and 'thetvdb://' in last_episode.guid:
                tvdb_id = last_episode.guid.split('thetvdb://')[1].split('?')[0].split('/')[0]
            else:
                tvdb_id = None

            if tvdb_id and tvdb_id in tvdb_ids:
                matching_episodes.append(last_episode)

        print("{}: Sorting list in correct order".format(playlist_name))

        for tvdb_id in tvdb_ids:
            for episode in matching_episodes:
                show_tvdb_id = episode.guid.split('thetvdb://')[1].split('?')[0].split('/')[0]
                if show_tvdb_id == tvdb_id:
                    sorted_shows.append(episode)
                    break;

        print("{}: Created shows list".format(playlist_name))

        loop_plex_users(plex, sorted_shows, playlist_name)
    else:
        print('{}: WARNING - Playlist is empty'.format(playlist_name))

def setup_movie_playlist(plex, imdb_ids, plex_movies, playlist_name):
    # check that the list is not empty
    if imdb_ids:
        # Create a list of matching movies
        print("{}: finding matching movies for playlist with count {}".format(playlist_name, len(imdb_ids)))
        matching_movies = []
        sorted_movies = []
        for movie in plex_movies:
            if movie.guid != NA and 'imdb://' in movie.guid:
                imdb_id = movie.guid.split('imdb://')[1].split('?')[0]
            else:
                imdb_id = None
                
            if imdb_id and imdb_id in imdb_ids:
                matching_movies.append(movie)

        print("{}: Sorting list in correct order".format(playlist_name))

        for imdb_id in imdb_ids:
            for movie in matching_movies:
                movie_imdb_id = movie.guid.split('imdb://')[1].split('?')[0]
                if movie_imdb_id == imdb_id:
                    sorted_movies.append(movie)
                    break;

        print("{}: Created movie list".format(playlist_name))

        loop_plex_users(plex, sorted_movies, playlist_name)
    else:
        print('{}: WARNING - Playlist is empty'.format(playlist_name))

def trakt_watched_imdb_id_list():
    # Get the weekly watched list
    print("Retrieving the Trakt weekly list...")
    imdb_ids = []

    headers = {
    'Content-Type': 'application/json',
    'trakt-api-version': '2',
    'trakt-api-key': TRAKT_API_KEY
    }

    request = Request('https://api.trakt.tv/movies/watched/weekly?page=1&limit={}'.format(TRAKT_NUM_MOVIES), headers=headers)
    response = urlopen(request)
    trakt_movies = json.load(response)

    # loop through movies and add movies to list if match
    for movie in trakt_movies:
        imdb_ids.append(movie['movie']['ids']['imdb'])

    return imdb_ids

def trakt_popular_imdb_id_list():
    # Get the weekly watched list
    print("Retrieving the Trakt popular list...")
    imdb_ids = []

    headers = {
    'Content-Type': 'application/json',
    'trakt-api-version': '2',
    'trakt-api-key': TRAKT_API_KEY
    }

    request = Request('https://api.trakt.tv/movies/popular?page=1&limit={}'.format(TRAKT_NUM_MOVIES), headers=headers)
    response = urlopen(request)
    trakt_movies = json.load(response)

    # loop through movies and add movies to list if match
    for movie in trakt_movies:
        imdb_ids.append(movie['ids']['imdb'])

    return imdb_ids

def trakt_watched_show_imdb_id_list():
    # Get the weekly watched list
    print("Retrieving the Trakt weekly list...")
    tvdb_ids = []

    headers = {
    'Content-Type': 'application/json',
    'trakt-api-version': '2',
    'trakt-api-key': TRAKT_API_KEY
    }

    request = Request('https://api.trakt.tv/shows/watched/weekly?page=1&limit={}'.format(TRAKT_NUM_SHOWS), headers=headers)
    response = urlopen(request)
    trakt_show = json.load(response)

    # loop through movies and add movies to list if match
    for show in trakt_show:
        tvdb_ids.append(str(show['show']['ids']['tvdb']))

    return tvdb_ids

def trakt_popular_show_imdb_id_list():
    # Get the weekly watched list
    print("Retrieving the Trakt popular list...")
    tvdb_ids = []

    headers = {
    'Content-Type': 'application/json',
    'trakt-api-version': '2',
    'trakt-api-key': TRAKT_API_KEY
    }

    request = Request('https://api.trakt.tv/shows/popular?page=1&limit={}'.format(TRAKT_NUM_SHOWS), headers=headers)
    response = urlopen(request)
    trakt_show = json.load(response)

    # loop through movies and add movies to list if match
    for show in trakt_show:
        tvdb_ids.append(str(show['ids']['tvdb']))

    return tvdb_ids

def imdb_top_imdb_id_list(list_url):
    # Get the IMDB Top 250 list
    print("Retrieving the IMDB Top 250 list...")
    tree = parse(list_url)
    top_250_ids = tree.xpath("//table[contains(@class, 'chart')]//td[@class='ratingColumn']/div//@data-titleid")

    return top_250_ids

def run_movies_lists(plex):
    # Get list of movies from the Plex server
    print("Retrieving a list of movies from the '{library}' library in Plex...".format(library=MOVIE_LIBRARY_NAME))
    try:
        movie_library = plex.library.section(MOVIE_LIBRARY_NAME)
        all_movies = movie_library.all()
    except:
        print("The '{library}' library does not exist in Plex.".format(library=MOVIE_LIBRARY_NAME))
        print("Exiting script.")
        return [], 0

    print("Retrieving new lists")
    trakt_weekly_imdb_ids = trakt_watched_imdb_id_list()
    trakt_popular_imdb_ids = trakt_popular_imdb_id_list()
    imdb_top_movies_ids = imdb_top_imdb_id_list(IMDB_CHART_URL)

    print("setting up lists")
    setup_movie_playlist(plex, trakt_weekly_imdb_ids, all_movies, TRAKT_WEEKLY_PLAYLIST_NAME)
    setup_movie_playlist(plex, trakt_popular_imdb_ids, all_movies, TRAKT_POPULAR_PLAYLIST_NAME)
    setup_movie_playlist(plex, imdb_top_movies_ids, all_movies, IMDB_PLAYLIST_NAME)

def run_show_lists(plex):
    # Get list of shows from the Plex server
    print("Retrieving a list of movies from the '{library}' library in Plex...".format(library=SHOW_LIBRARY_NAME))
    try:
        show_library = plex.library.section(SHOW_LIBRARY_NAME)
        all_shows = show_library.all()
    except:
        print("The '{library}' library does not exist in Plex.".format(library=SHOW_LIBRARY_NAME))
        print("Exiting script.")
        return [], 0

    print("Retrieving new lists")
    trakt_weekly_show_imdb_ids = trakt_watched_show_imdb_id_list()
    trakt_popular_show_imdb_ids = trakt_popular_show_imdb_id_list()

    print("setting up lists")
    setup_show_playlist(plex, trakt_weekly_show_imdb_ids, all_shows, TRAKT_WEEKLY_SHOW_PLAYLIST_NAME)
    setup_show_playlist(plex, trakt_popular_show_imdb_ids, all_shows, TRAKT_POPULAR_SHOW_PLAYLIST_NAME)

def list_updater():
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    except:
        print("No Plex server found at: {base_url} or bad plex token code".format(base_url=PLEX_URL))
        print("Exiting script.")
        raw_input("press enter to exit")
        return [], 0

    run_movies_lists(plex)
    run_show_lists(plex)


if __name__ == "__main__":
    print("===================================================================")
    print("   Automated Playlist to Plex script   ")
    print("===================================================================\n")

    list_updater()

    print("\n===================================================================")
    print("                               Done!                               ")
    print("===================================================================\n")
