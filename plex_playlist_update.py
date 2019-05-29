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
from classes.PlaylistSummary import PlaylistSummary
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

START_TIME = time.time()
PLEX_URL = config.get('Plex', 'plex-host')
PLEX_TOKEN = config.get('Plex', 'plex-token')
MOVIE_LIBRARY_NAME = config.get('Plex', 'movie-library')
SHOW_LIBRARY_NAME = config.get('Plex', 'tv-library')
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
try:
    MISSING_COLUMNS = int(config.get('Plex', 'missing_columns'))
except:
    MISSING_COLUMNS = 4
try:
    TRAKT_API_KEY = config.get('Trakt', 'api-key')
except:
    TRAKT_API_KEY = None
try:
    TRAKT_MOVIE_LISTS = json.loads(config.get('Trakt', 'trakt-movie-list'))
except:
    TRAKT_MOVIE_LISTS = []
try:
    TRAKT_SHOW_LISTS = json.loads(config.get('Trakt', 'trakt-tv-list'))
except:
    TRAKT_SHOW_LISTS = []
try:
    IMDB_LISTS = json.loads(config.get('IMDb', 'imdb-lists'))
except:
    IMDB_LISTS = []
try:
    DISCORD_URL = config.get('Discord', 'webhook_url')
except:
    DISCORD_URL = None

####### CODE HERE (Nothing to change) ############

def log_timer(marker = "", verbose = 0):
    if VERBOSE >= verbose and marker:
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


def loop_plex_users(plex, shared_users, imdb_tt_list, playlist_name):
    if not imdb_tt_list:
        print("{}: list EMPTY so will only be REMOVED and not created".format(playlist_name))

    # update my list
    create_playlists(plex, imdb_tt_list, playlist_name)
    print("{}: Playlist made for primary user".format(playlist_name))

    # update list for shared users
    if SYNC_WITH_SHARED_USERS:
        for user in shared_users:
            user_token = shared_users[user]
            user_plex = PlexServer(baseurl=PLEX_URL, token=user_token, timeout=PLEX_TIMEOUT)
            create_playlists(user_plex, imdb_tt_list, playlist_name)
            print("{}: playlist made for user {}".format(playlist_name, user))

    else:
        print("Skipping adding to shared users")

def get_tvdb_id(show):
    tvdb_id = None
    last_episode = show.episodes()[-1]
    if last_episode.guid != NA and 'thetvdb://' in last_episode.guid:
        tvdb_id = last_episode.guid.split('thetvdb://')[1].split('?')[0].split('/')[0]
    return tvdb_id


def setup_show_playlist(plex, shared_users, tvdb_ids, plex_shows, playlist_name, kind):
    if tvdb_ids:
        summary = PlaylistSummary("tvdb", playlist_name, tvdb_ids)
        # Create a list of matching shows using last episode
        print("{}: finding matching episodes for playlist with count {}".format(playlist_name, len(tvdb_ids)))
        matching_episodes = []
        matching_episode_ids = []
        sorted_episodes = []
        matching_shows = []
        for show in plex_shows:
            tvdb_id = get_tvdb_id(show)

            if tvdb_id and tvdb_id in tvdb_ids:
              matching_shows.append(show)
              matching_episodes.append(show.episodes()[-1])
              matching_episode_ids.append(tvdb_id)

        for tvdb_id in tvdb_ids:
            for episode in matching_episodes:
                show_tvdb_id = episode.guid.split(
                    'thetvdb://')[1].split('?')[0].split('/')[0]
                if show_tvdb_id == tvdb_id:
                    sorted_episodes.append(episode)
                    break

        summary.matching_ids = matching_episode_ids
        summary.sorted_episodes = sorted_episodes

        if kind == "collection":
          add_items_to_collection(plex, matching_shows, playlist_name)
        else:
          loop_plex_users(plex, shared_users, summary.sorted_episodes, playlist_name)

        summary.found_info()
        if SHOW_MISSING:
            summary.missing_info(MISSING_COLUMNS)

        if DISCORD_URL:
            summary.send_to_discord(DISCORD_URL)
    else:
        print('{}: WARNING - Playlist is empty'.format(playlist_name))



def get_imdb_id(movie):
    try:
        # com.plexapp.agents.imdb://tt0137523?lang=en
        imdb_id = "tt" + re.search(r'tt(\d+)\?', movie.guid).group(1)
    except:
        imdb_id = None
    return imdb_id

def append_movie_id_dict(movie, movie_id_dict):
    imdb_id = get_imdb_id(movie)
    if imdb_id != None:
        movie_id_dict[imdb_id] = movie
    return movie_id_dict

def show_dict_progress(curnum, total, status='adding movies'):
    bar_length = 50
    filled_len = int(round(bar_length * curnum / float(total)))
    percents = round(100.0 * (curnum / float(total)), 1)
    bar = '=' * filled_len + '-' * (bar_length - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', "{0} of {1}".format(curnum, total)))
    sys.stdout.flush()

def create_movie_id_dict(movies):
    movie_id_dict = {}
    count = len(movies)
    cur = 1
    log_timer("start creating movie id dict", 3)
    for movie in movies:
        log_timer("start append movie id dict", 3)
        movie_id_dict = append_movie_id_dict(movie, movie_id_dict)
        show_dict_progress(cur, count)
        cur += 1
    print("\ncached plex movies")
    log_timer("finished creating movie id dict", 3)
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

def add_items_to_collection(plex, medias, tag):
    for media in medias:
      media.addCollection(tag)


def setup_movie_playlist(plex, shared_users, imdb_ids, movie_id_dict, playlist_name, kind):
    if imdb_ids:
        summary = PlaylistSummary("imdb", playlist_name, imdb_ids)
        print("{0}: finding matching movies for playlist with count {1}".format(
            playlist_name,
            len(imdb_ids)
        ))

        matches = get_matching_movies(imdb_ids, movie_id_dict)
        summary.matching_movies = matches[0]
        summary.matching_ids = matches[1]

        if kind == "collection":
          add_items_to_collection(plex, summary.matching_movies, summary.name)
        else:
          loop_plex_users(plex, shared_users, summary.matching_movies, summary.name)

        summary.found_info()
        if SHOW_MISSING:
            summary.missing_info(MISSING_COLUMNS)

        if DISCORD_URL:
            summary.send_to_discord(DISCORD_URL)

    else:
        print("{0}: WARNING - Playlist is empty".format(playlist_name))


def trakt_tv_list_ids(trakt_json, json_type):
    tvdb_ids = []
    if json_type == "watched":
        for show in trakt_json:
            tvdb_ids.append(str(show['show']['ids']['tvdb']))
    if json_type == "popular":
        for show in trakt_json:
            tvdb_ids.append(str(show['ids']['tvdb']))
    return tvdb_ids

def trakt_movie_list_ids(trakt_json, json_type):
    imdb_ids = []
    if json_type == "watched":
        for movie in trakt_json:
            imdb_ids.append(movie['movie']['ids']['imdb'])
    if json_type == "popular":
        for movie in trakt_json:
            imdb_ids.append(movie['ids']['imdb'])
    return imdb_ids

def trakt_show_list_loop(plex, shared_users, all_shows):
    for runlist in TRAKT_SHOW_LISTS:
        kind = runlist.get("kind", 'playlist')
        print("{0}: STARTING PLAYLIST - TYPE: {2} - URL: {1} - KIND: {3}".format(
            runlist["title"],
            runlist["url"],
            runlist["type"],
            kind
        ))
        headers = {
            'Content-Type': 'application/json',
            'trakt-api-version': '2',
            'trakt-api-key': TRAKT_API_KEY
        }
        request = Request('{}?page=1&limit={}'.format(runlist["url"], runlist["limit"]), headers=headers)
        try:
            response = urlopen(request)
            trakt_shows = json.load(response)
        except:
            print("Bad Trakt Code")
            return []

        tvdb_ids = trakt_tv_list_ids(trakt_shows, runlist["type"])
        setup_show_playlist(plex, shared_users, tvdb_ids, all_shows, runlist["title"], kind)


def trakt_movie_list_loop(plex, shared_users, movie_id_dict):
    for runlist in TRAKT_MOVIE_LISTS:
        kind = runlist.get("kind", 'playlist')
        print("{0}: STARTING PLAYLIST - TYPE: {2} - URL: {1} - KIND: {3}".format(
            runlist["title"],
            runlist["url"],
            runlist["type"],
            kind
        ))
        headers = {
            'Content-Type': 'application/json',
            'trakt-api-version': '2',
            'trakt-api-key': TRAKT_API_KEY
        }
        request = Request('{}?page=1&limit={}'.format(runlist["url"], runlist["limit"]), headers=headers)
        try:
            response = urlopen(request)
            trakt_movies = json.load(response)
        except:
            print("Bad Trakt Code")
            return []

        imdb_ids = trakt_movie_list_ids(trakt_movies, runlist["type"])
        setup_movie_playlist(plex, shared_users, imdb_ids, movie_id_dict, runlist["title"], kind)

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
    if type == "custom":
        return tree.xpath("//h1[contains(@class, 'header list-name')]")[0].text.strip()

    return

def imdb_list_loop(plex, shared_users, movie_id_dict):
    for runlist in IMDB_LISTS:
        kind = runlist.get("kind", 'playlist')
        page = requests.get(runlist["url"])
        tree = html.fromstring(page.content)

        if runlist["title"]:
            title = runlist["title"]
        else:
            title = imdb_list_name(tree, runlist["type"])
        if not title:
            print("SKIPPING LIST because no title found")
            continue

        print("{0}: STARTING PLAYLIST - TYPE: {2} - URL: {1}".format(
            title,
            runlist["url"],
            runlist["type"]
        ))

        ids = imdb_list_ids(tree, runlist["type"])
        setup_movie_playlist(plex, shared_users, ids, movie_id_dict, title, kind)

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

    print("Found {0} movies total in 'all movies' list from Plex...".format(
        len(all_movies)
    ))

    print("Creating movie dictionary based on ID")
    movie_id_dict = create_movie_id_dict(all_movies)

    print("Retrieving new lists")
    if TRAKT_API_KEY:
        trakt_movie_list_loop(plex, shared_users, movie_id_dict)
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

    print("Found {0} show total in 'all shows' list from Plex...".format(
        len(all_shows)
    ))

    if TRAKT_API_KEY:
        trakt_show_list_loop(plex, shared_users, all_shows)
    else:
        print("No Trakt API key, skipping lists")


def list_remover(plex, shared_users, playlist_name):
    # update my list
    print("{}: removing playlist for script user".format(playlist_name))
    remove_playlist(plex, playlist_name)

    # update list for shared users
    if SYNC_WITH_SHARED_USERS:
        for user in shared_users:
            print("{0}: removing playlist for user {1}".format(
                playlist_name,
                user
            ))
            user_token = shared_users[user]
            user_plex = PlexServer(baseurl=PLEX_URL, token=user_token, timeout=PLEX_TIMEOUT)
            remove_playlist(user_plex, playlist_name)
    else:
        print("Skipping removal from shared users")

def remove_lists(plex, shared_users):
    for runlist in IMDB_LISTS:
        if runlist["title"]:
            title = runlist["title"]
        else:
            page = requests.get(runlist["url"])
            tree = html.fromstring(page.content)
            title = imdb_list_name(tree, runlist["type"])
        if not title:
            print("SKIPPING LIST because no title found")
            continue
        print("Removing IMDB custom playlist '{0}'".format(
            title
        ))
        list_remover(plex, shared_users, title)
    for runlist in TRAKT_MOVIE_LISTS:
        print("Removing IMDB custom playlist '{0}'".format(
            runlist["title"]
        ))
        list_remover(plex, shared_users, runlist["title"])


def get_all_users(plex):
    machineID = plex.machineIdentifier
    headers = {'Accept': 'application/json', 'X-Plex-Token': PLEX_TOKEN}
    result = requests.get('https://plex.tv/api/servers/{server_id}/shared_servers?X-Plex-Token={token}'.format(server_id=machineID, token=PLEX_TOKEN), headers=headers)
    xmlData = xmltodict.parse(result.content)
    
    result2 = requests.get('https://plex.tv/api/users', headers=headers)
    xmlData2 = xmltodict.parse(result2.content)

    users = {}
    user_ids = {}
    if 'User' in xmlData2['MediaContainer'].keys():
        # has atleast 1 shared user generally
        user_ids = {plex_user['@id']: plex_user.get('@username', plex_user.get('@title')) for plex_user in xmlData2['MediaContainer']['User']}


    if 'SharedServer' in xmlData['MediaContainer']:
        # has atlease 1 shared server
        if isinstance(xmlData['MediaContainer']['SharedServer'],list):
            # more than 1 shared user
            for server_user in xmlData['MediaContainer']['SharedServer']:
                users[user_ids[server_user['@userID']]] = server_user['@accessToken']
        else:
            # only 1 shared user
            server_user = xmlData['MediaContainer']['SharedServer']
            users[user_ids[server_user['@userID']]] = server_user['@accessToken']

    return users


def get_user_tokens(plex):
    users = get_all_users(plex)
    allowed_users = {}
    for user in users:
        if (not ALLOW_SYNCED_USERS or user in ALLOW_SYNCED_USERS) and user not in NOT_ALLOW_SYNCED_USERS:
            allowed_users[user] = users[user]

    return allowed_users

def list_updater(plex):
    users = get_user_tokens(plex)

    log_output("shared users list: {}".format(users), 1)
    
    run_movies_lists(plex, users)
    run_show_lists(plex, users)

if __name__ == "__main__":
    print("===================================================================")
    print("   Automated Playlist to Plex script   ")
    print("===================================================================\n")

    if (len(sys.argv) == 1 or sys.argv[1] not in ['run', 'show_users', 'show_allowed', 'remove_playlist', 'remove_all_playlists', 'discord_test']):
        print("""
Please use one of the following commands:
    run - Will start the normal process from your settings
    show_users - will give you a list of users to copy and paste to your settings file
    show_allowed - will give you a list of users your script will create playlists on
    remove_playlist - needs a second argument with playlist name to remove
    remove_all_playlists - will remove all playlists setup in the settings
    discord_test - send a test to your discord channel to make sure it works
    
    ex:
    python {0} run
    python {0} remove_playlist somename
    """.format(sys.argv[0]))
        sys.exit()

    # login to plex here.  All commands will need it
    try:
        plex = PlexServer(baseurl=PLEX_URL, token=PLEX_TOKEN, timeout=PLEX_TIMEOUT)
    except:
        print("No Plex server found at: {base_url} or bad plex token code".format(base_url=PLEX_URL))
        input("press enter to exit")
        sys.exit()


    # run standard
    if sys.argv[1] == 'run':
        list_updater(plex)

    # display available users
    if sys.argv[1] == 'show_users':
        users = get_all_users(plex)
        print('{} shared users'.format(len(users)))
        for key, value in users.items():
            print('Username: {}'.format(key))

    if sys.argv[1] == 'show_allowed':
        users = get_user_tokens(plex)
        print('{} shared users'.format(len(users)))
        for key, value in users.items():
            print('Username: {}'.format(key))

    if sys.argv[1] == 'remove_playlist':
        if len(sys.argv) >= 3:
            print('removing playlist {}'.format(sys.argv[2]))
            list_remover(plex, get_user_tokens(plex), sys.argv[2])
        else:
            print("Please supply a playlist name for the second command argument")

    if sys.argv[1] == 'remove_all_playlists':
        remove_lists(plex, get_user_tokens(plex))

    if sys.argv[1] == 'discord_test':
        print("Testing sending to discord")
        print("using URL: {}".format(DISCORD_URL))

        message = {}
        first_part = {}
        first_part["title"] = "Playlists connected"
        message['embeds'] = [first_part]
        json_data = json.dumps(message)
        r = requests.post(DISCORD_URL, headers={"Content-Type":"application/json"}, json=message)
        if r.status_code == 204:
            print("You should see a message in discord.")




    print("\n===================================================================")
    print("                               Done!                               ")

    log_timer()

    print("===================================================================\n")
