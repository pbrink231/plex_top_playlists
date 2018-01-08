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

import time
import json
import os
import requests
import subprocess
import time
import xmltodict
import ConfigParser
from lxml.html import parse
from plexapi.server import PlexServer
#from plexapi.utils import NA
NA=""

from urllib2 import Request, urlopen

config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'settings.ini')
config = ConfigParser.SafeConfigParser()
config.read(config_file_path)

PLEX_URL = config.get('Plex', 'plex-host')
PLEX_TOKEN = config.get('Plex', 'plex-token')
MOVIE_LIBRARY_NAME = config.get('Plex', 'movie-library')
SHOW_LIBRARY_NAME = config.get('Plex', 'tv-library')
REMOVE_ONLY = config.getboolean('Plex', 'remove')
SYNC_WITH_SHARED_USERS = config.getboolean('Plex', 'shared')
ALLOW_SYNCED_USERS = json.loads(config.get('Plex', 'users'))
NOT_ALLOW_SYNCED_USERS = json.loads(config.get('Plex', 'not_users'))
TRAKT_API_KEY = config.get('Trakt', 'api-key')
TRAKT_NUM_MOVIES = config.get('Trakt', 'movie-total')
TRAKT_WEEKLY_PLAYLIST_NAME = config.get('Trakt', 'weekly-movie-name')
TRAKT_POPULAR_PLAYLIST_NAME = config.get('Trakt', 'popular-movie-name')
TRAKT_NUM_SHOWS = config.get('Trakt', 'tv-total')
TRAKT_WEEKLY_SHOW_PLAYLIST_NAME = config.get('Trakt', 'weekly-tv-name')
TRAKT_POPULAR_SHOW_PLAYLIST_NAME = config.get('Trakt', 'popular-tv-name')
IMDB_CHART_URL = config.get('IMDb', 'chart-url')
IMDB_SEARCH_URL = ''.join([config.get('IMDb', 'search-url'),'&count=',config.get('IMDb', 'search-total')])
IMDB_PLAYLIST_NAME = config.get('IMDb', 'playlist-name')
IMDB_SEARCH_NAME = config.get('IMDb', 'search-list-name')
IMDB_CUSTOM_URL = config.get('IMDb', 'list-url')
IMDB_CUSTOM_LIST = config.get('IMDb', 'list-name')

####### CODE HERE (Nothing to change) ############

def get_user_tokens(server_id):
    headers = {'Accept': 'application/json', 'X-Plex-Token': PLEX_TOKEN}
    result = requests.get('https://plex.tv/api/servers/{server_id}/shared_servers?X-Plex-Token={token}'.format(server_id=server_id, token=PLEX_TOKEN), headers=headers)
    xmlData = xmltodict.parse(result.content)
    users = {user['@username']: user['@accessToken'] for user in xmlData['MediaContainer']['SharedServer']}

    return users

def remove_playlist(plex, playlist_name):
    for playlist in plex.playlists():
        if playlist.title == playlist_name:
            try:
                playlist.delete()
                #print("{}: Playlist deleted".format(playlist_name))
            except:
                print("ERROR - cannot delete playlist: {}".format(playlist_name))
                return None

def create_playlists(plex, list, playlist_name):
    # Remove old playlists
    #print('{}: Checking if playlist exist to delete if needed'.format(playlist_name))
    remove_playlist(plex, playlist_name)

    plex.createPlaylist(playlist_name, list)
    #print("{}: playlist created".format(playlist_name))

def loop_plex_users(plex, list, playlist_name):
    #update my list
    create_playlists(plex, list, playlist_name)

    #update list for shared users
    if SYNC_WITH_SHARED_USERS:
        plex_users = get_user_tokens(plex.machineIdentifier)
        for user in plex_users:
            if (not ALLOW_SYNCED_USERS or user in ALLOW_SYNCED_USERS) and user not in NOT_ALLOW_SYNCED_USERS:
                print("{}: updating playlist for user {}".format(playlist_name, user))
                user_token = plex_users[user]
                user_plex = PlexServer(baseurl=PLEX_URL, token=user_token, timeout=120)
                create_playlists(user_plex, list, playlist_name)
    else:
        print("Skipping adding to shared users")


def setup_show_playlist(plex, tvdb_ids, plex_shows, playlist_name):
    if tvdb_ids:
        # Create a list of matching shows using last episode
        print("{}: finding matching episodes for playlist with count {}".format(playlist_name, len(tvdb_ids)))
        matching_episodes = []
        matching_episode_ids = []
        sorted_shows = []
        for show in plex_shows:
            last_episode = show.episodes()[-1]
            if last_episode.guid != NA and 'thetvdb://' in last_episode.guid:
                tvdb_id = last_episode.guid.split('thetvdb://')[1].split('?')[0].split('/')[0]
            else:
                tvdb_id = None

            if tvdb_id and tvdb_id in tvdb_ids:
                matching_episodes.append(last_episode)
                matching_episode_ids.append(tvdb_id)

        missing_episode_ids = list(set(tvdb_ids) - set(matching_episode_ids))
        print("I found {match_len} of your episode IDs that matched the TVDB IDs top {tvdb_len} list".format(match_len=len(matching_episode_ids), tvdb_len=len(tvdb_ids)))
        print("That means you are missing {missing_len} of the TVDB IDs top {tvdb_len} list".format(missing_len=len(missing_episode_ids), tvdb_len=len(tvdb_ids)))
        if len(missing_episode_ids) > 0:
            print("The TVDB IDs are listed below .. You can copy/paste this info and put into sonarr ..")
            for tvdb_id in missing_episode_ids:
                print("tvdb: {}".format(tvdb_id))

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

def get_imdb_id(movie=None):
    imdb_id = None
    if movie.guid != NA and 'imdb://' in movie.guid:
        imdb_id = movie.guid.split('imdb://')[1].split('?')[0]
    return imdb_id

def append_movie_id_dict(movie=None, movie_id_dict=None):
    imdb_id = get_imdb_id(movie=movie)
    if imdb_id != None:
        movie_id_dict[imdb_id] = movie
        # print "Appending movie id {0}".format(
        #     imdb_id
        # )
    return movie_id_dict

def get_matching_movies(imdb_ids=None, movie_id_dict=None):
    movies = []
    movie_ids = []

    for imdb_id in imdb_ids:
        if movie_id_dict[imdb_id]:
            movies.append(movie_id_dict[imdb_id])
            movie_ids.append(imdb_id)
    return {
        movies: movies,
        movie_ids: movie_ids
    }

def setup_movie_playlist(plex, imdb_ids, plex_movies, playlist_name):
    # check that the list is not empty
    if imdb_ids:
        # Create a list of matching movies
        print("{}: finding matching movies for playlist with count {}".format(playlist_name, len(imdb_ids)))
        sorted_movies = []
        movie_id_dict = {}
        for movie in plex_movies:
            movie_id_dict = append_movie_id_dict(movie=movie, movie_id_dict=movie_id_dict)

        matches = get_matching_movies(
            imdb_ids=imdb_ids,
            movie_id_dict=movie_id_dict)

        matching_movies = matches.movies
        matching_movie_ids = matches.movie_ids

        missing_imdb_ids = list(set(imdb_ids) - set(matching_movie_ids))
        print("I found {match_len} of your movie IDs that matched the IMDB IDs top {imdb_len} list".format(match_len=len(matching_movie_ids), imdb_len=len(imdb_ids)))
        print("That means you are missing {missing_len} of the IMDB IDs top {imdb_len} list".format(missing_len=len(missing_imdb_ids), imdb_len=len(imdb_ids)))
        if len(missing_imdb_ids) > 0:
            print("The IMDB IDs are listed below .. You can copy/paste this info and put into radarr ..")
            for imdb_id in missing_imdb_ids:
                print("imdb: {}".format(imdb_id))

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
    try:
        response = urlopen(request)
        trakt_movies = json.load(response)

        # loop through movies and add movies to list if match
        for movie in trakt_movies:
            imdb_ids.append(movie['movie']['ids']['imdb'])
    except:
        print "Bad Trakt Code"
        return []

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

    try:
        request = Request('https://api.trakt.tv/movies/popular?page=1&limit={}'.format(TRAKT_NUM_MOVIES), headers=headers)
        response = urlopen(request)
        trakt_movies = json.load(response)

        # loop through movies and add movies to list if match
        for movie in trakt_movies:
            imdb_ids.append(movie['ids']['imdb'])
    except:
        print "Bad Trakt Code"
        return []

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
    try:
        request = Request('https://api.trakt.tv/shows/watched/weekly?page=1&limit={}'.format(TRAKT_NUM_SHOWS), headers=headers)
        response = urlopen(request)
        trakt_show = json.load(response)

        # loop through movies and add movies to list if match
        for show in trakt_show:
            tvdb_ids.append(str(show['show']['ids']['tvdb']))
    except:
        print "Bad Trakt Code"
        return []

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

    try:
        request = Request('https://api.trakt.tv/shows/popular?page=1&limit={}'.format(TRAKT_NUM_SHOWS), headers=headers)
        response = urlopen(request)
        trakt_show = json.load(response)

        # loop through movies and add movies to list if match
        for show in trakt_show:
            tvdb_ids.append(str(show['ids']['tvdb']))
    except:
        print "Bad Trakt Code"
        return []

    return tvdb_ids

def imdb_top_imdb_id_list(list_url):
    # Get the IMDB Top 250 list
    print("Retrieving the IMDB Top 250 list...")
    tree = parse(list_url)
    top_250_ids = tree.xpath("//table[contains(@class, 'chart')]//td[@class='ratingColumn']/div//@data-titleid")

    return top_250_ids

def imdb_search_list(search_url):
     # Get the IMDB Search list
     print("Retrieving the IMDB Search list...")
     tree = parse(search_url)
     search_ids = tree.xpath("//img[@class='loadlate']/@data-tconst")

     return search_ids

def imdb_custom_list(custom_url):
     # Get the IMDB Custom list
     print("Retrieving the IMDB Custom list...")
     tree = parse(custom_url)
     custom_ids = tree.xpath("//div[contains(@class, 'hover-over-image')]/@data-const")

     return custom_ids

def run_movies_lists(plex):
    # Get list of movies from the Plex server
    # split into array
    movie_libs = MOVIE_LIBRARY_NAME.split(",")
    all_movies = []

    # loop movie lib array
    for lib in movie_libs:
        lib = lib.strip()
        print("Retrieving a list of movies from the '{library}' library in Plex...".format(library=lib))
        try:
            movie_library = plex.library.section(lib)
            new_movies = movie_library.all()
            all_movies = all_movies + new_movies
            print("Added {length} movies to your 'all movies' list from the '{library}' library in Plex...".format(library=lib, length=len(new_movies)))
        except:
            print("The '{library}' library does not exist in Plex.".format(library=lib))
            print("Exiting script.")
            return [], 0

    print("Found {length} movies total in 'all movies' list from Plex...".format(length=len(all_movies)))
    print("Retrieving new lists")
    if TRAKT_API_KEY:
        trakt_weekly_imdb_ids = trakt_watched_imdb_id_list()
        trakt_popular_imdb_ids = trakt_popular_imdb_id_list()
        setup_movie_playlist(plex, trakt_weekly_imdb_ids, all_movies, TRAKT_WEEKLY_PLAYLIST_NAME)
        setup_movie_playlist(plex, trakt_popular_imdb_ids, all_movies, TRAKT_POPULAR_PLAYLIST_NAME)
    else:
        print("No Trakt API key, skipping lists")

    imdb_top_movies_ids = imdb_top_imdb_id_list(IMDB_CHART_URL)
    imdb_search_movies_ids = imdb_search_list(IMDB_SEARCH_URL)
    imdb_custom_movies_ids = imdb_custom_list(IMDB_CUSTOM_URL)
    setup_movie_playlist(plex, imdb_top_movies_ids, all_movies, IMDB_PLAYLIST_NAME)
    setup_movie_playlist(plex, imdb_search_movies_ids, all_movies, IMDB_SEARCH_NAME)
    setup_movie_playlist(plex, imdb_custom_movies_ids, all_movies, IMDB_CUSTOM_LIST)

def run_show_lists(plex):
    # Get list of shows from the Plex server
    # split into array
    show_libs = SHOW_LIBRARY_NAME.split(",")
    all_shows = []

    # loop movie lib array
    for lib in show_libs:
        lib = lib.strip()
        print("Retrieving a list of shows from the '{library}' library in Plex...".format(library=lib))
        try:
            show_library = plex.library.section(lib)
            new_shows = show_library.all()
            all_shows = all_shows + new_shows
            print("Added {length} shows to your 'all shows' list from the '{library}' library in Plex...".format(library=lib, length=len(new_shows)))
        except:
            print("The '{library}' library does not exist in Plex.".format(library=lib))
            print("Exiting script.")
            return [], 0

    print("Found {length} shows total in 'all shows' list from Plex...".format(length=len(all_shows)))
    print("Retrieving new lists")
    if TRAKT_API_KEY:
        trakt_weekly_show_imdb_ids = trakt_watched_show_imdb_id_list()
        trakt_popular_show_imdb_ids = trakt_popular_show_imdb_id_list()
        setup_show_playlist(plex, trakt_weekly_show_imdb_ids, all_shows, TRAKT_WEEKLY_SHOW_PLAYLIST_NAME)
        setup_show_playlist(plex, trakt_popular_show_imdb_ids, all_shows, TRAKT_POPULAR_SHOW_PLAYLIST_NAME)
    else:
        print("No Trakt API key, skipping lists")

def list_remover(plex, playlist_name):
    #update my list
    print("{}: removing playlist for script user".format(playlist_name))
    remove_playlist(plex, playlist_name)

    #update list for shared users
    if SYNC_WITH_SHARED_USERS:
        plex_users = get_user_tokens(plex.machineIdentifier)
        for user in plex_users:
            if (not ALLOW_SYNCED_USERS or user in ALLOW_SYNCED_USERS):
                print "{0}: removing playlist for user {1}".format(
                    playlist_name,
                    user
                )
                user_token = plex_users[user]
                user_plex = PlexServer(baseurl=PLEX_URL, token=user_token, timeout=120)
                remove_playlist(user_plex, playlist_name)
            else:
                print "{0}: NOT removing playlist for user {1}".format(
                    playlist_name,
                    user
                )
    else:
        print("Skipping removal from shared users")

def list_updater():
    try:
        plex = PlexServer(baseurl=PLEX_URL, token=PLEX_TOKEN, timeout=120)
    except:
        print("No Plex server found at: {base_url} or bad plex token code".format(base_url=PLEX_URL))
        print("Exiting script.")
        raw_input("press enter to exit")
        return [], 0

    if REMOVE_ONLY:
        list_remover(plex, TRAKT_WEEKLY_PLAYLIST_NAME)
        list_remover(plex, TRAKT_POPULAR_PLAYLIST_NAME)
        list_remover(plex, TRAKT_WEEKLY_SHOW_PLAYLIST_NAME)
        list_remover(plex, TRAKT_POPULAR_SHOW_PLAYLIST_NAME)
        list_remover(plex, IMDB_PLAYLIST_NAME)
        list_remover(plex, IMDB_SEARCH_NAME)
        list_remover(plex, IMDB_CUSTOM_LIST)
    else:
        run_movies_lists(plex)
        run_show_lists(plex)

if __name__ == "__main__":
    start_time = time.time()

    print("===================================================================")
    print("   Automated Playlist to Plex script   ")
    print("===================================================================\n")

    list_updater()

    print("\n===================================================================")
    print("                               Done!                               ")
    print("--- %s seconds ---" % (time.time() - start_time))
    print("===================================================================\n")
