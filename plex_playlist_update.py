#!/usr/bin/env python

# a python test script
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#         Automated Ranked Playlists - VikingGawd
#
#                         *** Use at your own risk! ***
#   *** I am not responsible for damages to your Plex server or libraries. ***
#
# ------------------------------------------------------------------------------

import time
import re
import json
import os
import requests
import subprocess
import time
import xmltodict
import configparser
import sys
from lxml import html
from plexapi.server import PlexServer
from urllib.request import Request, urlopen
NA = ""

config_file_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'settings.ini')
exists = os.path.isfile(config_file_path)
if exists:
    print("Using settings file")
else:
    print("Please create a settings.ini file in the same folder as plex_playlist_update.py")
    sys.exit("No settings.ini file")

config = configparser.SafeConfigParser()
config.read(config_file_path)

PLEX_URL = config.get('Plex', 'plex-host')
PLEX_TOKEN = config.get('Plex', 'plex-token')
MOVIE_LIBRARY_NAME = config.get('Plex', 'movie-library')
SHOW_LIBRARY_NAME = config.get('Plex', 'tv-library')
REMOVE_ONLY = config.getboolean('Plex', 'remove')
SYNC_WITH_SHARED_USERS = config.getboolean('Plex', 'shared')
ALLOW_SYNCED_USERS = json.loads(config.get('Plex', 'users'))
NOT_ALLOW_SYNCED_USERS = json.loads(config.get('Plex', 'not_users'))
try:
    VERBOSE = int(config.get('Plex', 'verbose'))
except:
    VERBOSE = 0
try:
    PLEX_TIMEOUT = int(config.get('Plex', 'timeout'))
except:
    PLEX_TIMEOUT = 300
try:
    SHOW_MISSING = config.getboolean('Plex', 'show_missing')
except:
    SHOW_MISSING = False
TRAKT_API_KEY = config.get('Trakt', 'api-key')
TRAKT_NUM_MOVIES = config.get('Trakt', 'movie-total')
TRAKT_WEEKLY_PLAYLIST_NAME = config.get('Trakt', 'weekly-movie-name')
TRAKT_POPULAR_PLAYLIST_NAME = config.get('Trakt', 'popular-movie-name')
TRAKT_NUM_SHOWS = config.get('Trakt', 'tv-total')
TRAKT_WEEKLY_SHOW_PLAYLIST_NAME = config.get('Trakt', 'weekly-tv-name')
TRAKT_POPULAR_SHOW_PLAYLIST_NAME = config.get('Trakt', 'popular-tv-name')
IMDB_LISTS = json.loads(config.get('IMDb', 'imdb-lists'))
START_TIME = time.time()

####### CODE HERE (Nothing to change) ############

def log_timer(marker = "", verbose = 0):
    if verbose >= VERBOSE and marker:
        print("{:.4f} -- {}".format(
            (time.time() - START_TIME),
            marker
        ))

def log_output(text, verbose):
    if VERBOSE >= verbose and text:
        print(text)


def remove_playlist(plex, playlist_name):
    for playlist in plex.playlists():
        if playlist.title == playlist_name:
            try:
                playlist.delete()
                #print("{}: Playlist deleted".format(playlist_name))
            except:
                print("ERROR - cannot delete playlist: {}".format(playlist_name))
                return None

def create_playlists(plex, runlist, playlist_name):
    try:
        remove_playlist(plex, playlist_name)
        if runlist:
            plex.createPlaylist(playlist_name, runlist)
    except:
        print("""
        ERROR trying to create playlist '{0}'
        The number of movies/shows in the list provided was {1}
        """.format(
            playlist_name,
            len(runlist)
        ))


def loop_plex_users(plex, shared_users, list, playlist_name):
    if not list:
        print("{} is EMPTY so will only be REMOVED and not created".format(playlist_name))

    # update my list
    create_playlists(plex, list, playlist_name)

    # update list for shared users
    if SYNC_WITH_SHARED_USERS:
        for user in shared_users:
            print("{}: updating playlist for user {}".format(playlist_name, user))
            user_token = shared_users[user]
            user_plex = PlexServer(baseurl=PLEX_URL, token=user_token, timeout=PLEX_TIMEOUT)
            create_playlists(user_plex, list, playlist_name)
    else:
        print("Skipping adding to shared users")

def get_tvdb_id(show):
    tvdb_id = None
    last_episode = show.episodes()[-1]
    if last_episode.guid != NA and 'thetvdb://' in last_episode.guid:
        tvdb_id = last_episode.guid.split('thetvdb://')[1].split('?')[0].split('/')[0]
    return tvdb_id

def setup_show_playlist(plex, shared_users, tvdb_ids, plex_shows, playlist_name):
    if tvdb_ids:
        # Create a list of matching shows using last episode
        print("{}: finding matching episodes for playlist with count {}".format(playlist_name, len(tvdb_ids)))
        matching_episodes = []
        matching_episode_ids = []
        sorted_shows = []
        for show in plex_shows:
            tvdb_id = get_tvdb_id(show)

            if tvdb_id and tvdb_id in tvdb_ids:
                matching_episodes.append(show.episodes()[-1])
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
                show_tvdb_id = episode.guid.split(
                    'thetvdb://')[1].split('?')[0].split('/')[0]
                if show_tvdb_id == tvdb_id:
                    sorted_shows.append(episode)
                    break

        print("{}: Created shows list".format(playlist_name))

        loop_plex_users(plex, shared_users, sorted_shows, playlist_name)
    else:
        print('{}: WARNING - Playlist is empty'.format(playlist_name))



def get_imdb_id(movie):
    try:
        imdb_id = "tt" + re.search(r'tt(\d+)\?', movie.guid).group(1)
    except:
        imdb_id = None
    return imdb_id

def append_movie_id_dict(movie, movie_id_dict):
    log_timer("start append movie id dict")
    imdb_id = get_imdb_id(movie)
    if imdb_id != None:
        movie_id_dict[imdb_id] = movie
    log_timer("end append movie id dict")
    return movie_id_dict

def create_movie_id_dict(movies):
    movie_id_dict = {}
    log_timer("start create movie id dict", 3)
    for movie in movies:
        movie_id_dict = append_movie_id_dict(movie, movie_id_dict)
    log_timer("end create movie id dict", 3)
    return movie_id_dict

def get_matching_movies(imdb_ids, movie_id_dict):
    movies = []
    movie_ids = []
    for imdb_id in imdb_ids:
        if imdb_id in movie_id_dict:
            movies.append(movie_id_dict[imdb_id])
            movie_ids.append(imdb_id)
    returnme = []
    returnme.append(movies)
    returnme.append(movie_ids)
    return returnme

def print_imdb_info(matching_movie_ids, imdb_ids, playlist_name):
    missing_imdb_ids = list(set(imdb_ids) - set(matching_movie_ids))
    print("""
    {match_ids_len} of {imdb_ids_len} movies found in list:
      {playlist_name}
    That means you are MISSING:
      {miss_ids_len}
    """.format(
        playlist_name=playlist_name,
        match_ids_len=len(matching_movie_ids),
        imdb_ids_len=len(imdb_ids),
        miss_ids_len=len(missing_imdb_ids)
    ))
    print_missing_imdb_info(missing_imdb_ids)

def print_missing_imdb_info(missing_imdb_ids):
    if SHOW_MISSING and len(missing_imdb_ids) > 0:
        print("""
    The IMDB IDs are listed below .. You can
    copy/paste this info and put into radarr ..
        """)
        print('\t'.join(map(str,missing_imdb_ids)))
        #for imdb_id in missing_imdb_ids:
        #    print("imdb: {0}".format(imdb_id))

        print("\n\n")

def setup_movie_playlist2(plex, shared_users, imdb_ids, movie_id_dict, playlist_name):
    if imdb_ids:
        print("{0}: finding matching movies for playlist with count {1}".format(
            playlist_name,
            len(imdb_ids)
        ))

        matches = get_matching_movies(imdb_ids, movie_id_dict)
        matching_movies = matches[0]
        matching_movie_ids = matches[1]

        print_imdb_info(matching_movie_ids, imdb_ids, playlist_name)

        print("{}: Created movie list".format(playlist_name))
        log_timer()

        loop_plex_users(plex, shared_users, matching_movies, playlist_name)
    else:
        print("{0}: WARNING - Playlist is empty".format(playlist_name))


def trakt_watched_imdb_id_list():
    # Get the weekly watched list
    print("Retrieving the Trakt weekly list...")
    imdb_ids = []

    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version': '2',
        'trakt-api-key': TRAKT_API_KEY
    }

    request = Request(
        'https://api.trakt.tv/movies/watched/weekly?page=1&limit={}'.format(TRAKT_NUM_MOVIES), headers=headers)
    try:
        response = urlopen(request)
        trakt_movies = json.load(response)

        # loop through movies and add movies to list if match
        for movie in trakt_movies:
            imdb_ids.append(movie['movie']['ids']['imdb'])
    except:
        print("Bad Trakt Code")
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
        request = Request(
            'https://api.trakt.tv/movies/popular?page=1&limit={}'.format(TRAKT_NUM_MOVIES), headers=headers)
        response = urlopen(request)
        trakt_movies = json.load(response)

        # loop through movies and add movies to list if match
        for movie in trakt_movies:
            imdb_ids.append(movie['ids']['imdb'])
    except:
        print("Bad Trakt Code")
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
        request = Request(
            'https://api.trakt.tv/shows/watched/weekly?page=1&limit={}'.format(TRAKT_NUM_SHOWS), headers=headers)
        response = urlopen(request)
        trakt_show = json.load(response)

        # loop through movies and add movies to list if match
        for show in trakt_show:
            tvdb_ids.append(str(show['show']['ids']['tvdb']))
    except:
        print("Bad Trakt Code")
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
        request = Request(
            'https://api.trakt.tv/shows/popular?page=1&limit={}'.format(TRAKT_NUM_SHOWS), headers=headers)
        response = urlopen(request)
        trakt_show = json.load(response)

        # loop through movies and add movies to list if match
        for show in trakt_show:
            tvdb_ids.append(str(show['ids']['tvdb']))
    except:
        print("Bad Trakt Code")
        return []

    return tvdb_ids

def imdb_list_ids(tree, type):
    if type =="chart":
        return tree.xpath("//table[contains(@class, 'chart')]//td[@class='ratingColumn']/div//@data-titleid")
    if type =="search":
        return tree.xpath("//img[@class='loadlate']/@data-tconst")
    if type =="custom":
        return tree.xpath("//div[contains(@class, 'lister-item-image ribbonize')]/@data-tconst")
    return


def imdb_list_name(tree, type):
    if type == "chart":
        return tree.xpath("//h1[contains(@class, 'header')]")[0].text.strip()
    if type == "search":
        return tree.xpath("//h1[contains(@class, 'header')]")[0].text.strip()
    if type == "custome":
        return tree.xpath("//h1[contains(@class, 'header list-name')]")[0].text.strip()

    return

def imdb_list_loop(plex, shared_users, movie_id_dict):
    for list in IMDB_LISTS:
        page = requests.get(list["url"])
        tree = html.fromstring(page.content)

        if list["title"]:
            title = list["title"]
        else:
            title = imdb_list_name(tree, list["type"])
        if not title:
            print("SKIPPING LIST because no title found")
            continue

        print("Creating IMDB search playlist '{0}' using URL {1}".format(
            title,
            list["url"]
        ))

        ids = imdb_list_ids(tree, list["type"])
        setup_movie_playlist2(plex, shared_users, ids, movie_id_dict, title)

def run_movies_lists(plex, shared_users):
    # Get list of movies from the Plex server
    # split into array
    movie_libs = MOVIE_LIBRARY_NAME.split(",")
    all_movies = []
    log_timer()

    # loop movie lib array
    for lib in movie_libs:
        lib = lib.strip()
        print("Retrieving a list of movies from the '{library}' library in Plex...".format(library=lib))
        try:
            movie_library = plex.library.section(lib)
            new_movies = movie_library.all()
            all_movies = all_movies + new_movies
            print("Added {length} movies to your 'all movies' list from the '{library}' library in Plex...".format(library=lib, length=len(new_movies)))
            log_timer()
        except:
            print("The '{library}' library does not exist in Plex.".format(library=lib))
            print("Exiting script.")
            return [], 0

    print("Found {0} movies total in 'all movies' list from Plex...".format(
        len(all_movies)
    ))

    print("Creating movie dictionary based on ID")
    movie_id_dict = create_movie_id_dict(all_movies)

    print("Retrieving new lists")
    if TRAKT_API_KEY:
        trakt_weekly_imdb_ids = trakt_watched_imdb_id_list()
        trakt_popular_imdb_ids = trakt_popular_imdb_id_list()
        setup_movie_playlist2(plex, shared_users, trakt_weekly_imdb_ids, movie_id_dict, TRAKT_WEEKLY_PLAYLIST_NAME)
        setup_movie_playlist2(plex, shared_users, trakt_popular_imdb_ids, movie_id_dict, TRAKT_POPULAR_PLAYLIST_NAME)
    else:
        print("No Trakt API key, skipping lists")

    imdb_list_loop(plex, shared_users, movie_id_dict)

def run_show_lists(plex, shared_users):
    # Get list of shows from the Plex server
    # split into array
    show_libs = SHOW_LIBRARY_NAME.split(",")
    all_shows = []
    log_timer()
    # loop movie lib array
    for lib in show_libs:
        lib = lib.strip()
        print("Retrieving a list of shows from the '{library}' library in Plex...".format(library=lib))
        try:
            show_library = plex.library.section(lib)
            new_shows = show_library.all()
            all_shows = all_shows + new_shows
            print("Added {length} shows to your 'all shows' list from the '{library}' library in Plex...".format(library=lib, length=len(new_shows)))
            log_timer()
        except:
            print("The '{library}' library does not exist in Plex.".format(library=lib))
            print("Exiting script.")
            return [], 0

    print("Found {0} show total in 'all shows' list from Plex...").format(
        len(all_shows)
    )

    print("Retrieving new lists")
    if TRAKT_API_KEY:
        trakt_weekly_show_imdb_ids = trakt_watched_show_imdb_id_list()
        trakt_popular_show_imdb_ids = trakt_popular_show_imdb_id_list()
        setup_show_playlist(plex, shared_users, trakt_weekly_show_imdb_ids, all_shows, TRAKT_WEEKLY_SHOW_PLAYLIST_NAME)
        setup_show_playlist(plex, shared_users, trakt_popular_show_imdb_ids, all_shows, TRAKT_POPULAR_SHOW_PLAYLIST_NAME)
        # setup_show_playlist2(plex, trakt_weekly_show_imdb_ids, show_id_dict, TRAKT_WEEKLY_SHOW_PLAYLIST_NAME)
        # setup_show_playlist2(plex, trakt_popular_show_imdb_ids, show_id_dict, TRAKT_POPULAR_SHOW_PLAYLIST_NAME)
    else:
        print("No Trakt API key, skipping lists")


def list_remover(plex, shared_users, playlist_name):
    # update my list
    print("{}: removing playlist for script user".format(playlist_name))
    remove_playlist(plex, playlist_name)

    # update list for shared users
    if SYNC_WITH_SHARED_USERS:
        for user in shared_users:
            print("{0}: removing playlist for user {1}").format(
                playlist_name,
                user
            )
            user_token = shared_users[user]
            user_plex = PlexServer(baseurl=PLEX_URL, token=user_token, timeout=PLEX_TIMEOUT)
            remove_playlist(user_plex, playlist_name)
    else:
        print("Skipping removal from shared users")

def remove_lists(plex, shared_users):
    for list in IMDB_LISTS:
        if list["title"]:
            title = list["title"]
        else:
            page = requests.get(list["url"])
            tree = html.fromstring(page.content)
            title = imdb_list_name(tree, list["type"])
        if not title:
            print("SKIPPING LIST because no title found")
            continue
        print("Removing IMDB custom playlist '{0}'").format(
            title
        )
        list_remover(plex, shared_users, title)

def get_user_tokens(server_id):
    headers = {'Accept': 'application/json', 'X-Plex-Token': PLEX_TOKEN}
    result = requests.get('https://plex.tv/api/servers/{server_id}/shared_servers?X-Plex-Token={token}'.format(
        server_id=server_id, token=PLEX_TOKEN), headers=headers)
    xmlData = xmltodict.parse(result.content)
    
    result2 = requests.get('https://plex.tv/api/users', headers=headers)
    xmlData2 = xmltodict.parse(result2.content)

    user_ids = {user['@id']: user.get('@username', user.get('@title')) for user in xmlData2['MediaContainer']['User']}
    users = {user_ids[user['@userID']]: user['@accessToken'] for user in xmlData['MediaContainer']['SharedServer']}
    print(users)

    allowed_users = {}
    for user in users:
        if (not ALLOW_SYNCED_USERS or user in ALLOW_SYNCED_USERS) and user not in NOT_ALLOW_SYNCED_USERS:
            print(NOT_ALLOW_SYNCED_USERS)
            print(user)
            allowed_users[user] = users[user]

    return allowed_users

def list_updater():
    try:
        plex = PlexServer(baseurl=PLEX_URL, token=PLEX_TOKEN, timeout=PLEX_TIMEOUT)
    except:
        print("No Plex server found at: {base_url} or bad plex token code".format(
            base_url=PLEX_URL))
        print("Exiting script.")
        input("press enter to exit")
        return [], 0

    users = get_user_tokens(plex.machineIdentifier)

    log_output("users list: {}".format(users), 1)
    

    if REMOVE_ONLY:
        list_remover(plex, users, TRAKT_WEEKLY_PLAYLIST_NAME)
        list_remover(plex, users, TRAKT_POPULAR_PLAYLIST_NAME)
        list_remover(plex, users, TRAKT_WEEKLY_SHOW_PLAYLIST_NAME)
        list_remover(plex, users, TRAKT_POPULAR_SHOW_PLAYLIST_NAME)
        remove_lists(plex, users)
    else:
        run_movies_lists(plex, users)
        run_show_lists(plex, users)

if __name__ == "__main__":
    print("===================================================================")
    print("   Automated Playlist to Plex script   ")
    print("===================================================================\n")

    # allow some commands:
    # list all users
    # remove playlist by name
    # create a playlist specifically

    # run standard
    list_updater()

    print("\n===================================================================")
    print("                               Done!                               ")

    log_timer()

    print("===================================================================\n")
