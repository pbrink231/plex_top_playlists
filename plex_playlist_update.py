#!/usr/bin/env python
""" Main method to run playlist script along with helpful commands """
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

import sys
import json
import requests

import global_vars

# from classes.ListItem import ListItem
from functions.users import get_all_users, get_user_tokens
from functions.logger import log_timer
from functions.sources.imdb import imdb_list_loop, get_imdb_info
from functions.sources.trakt import trakt_list_loop
from functions.playlists import remove_shared_playlist, remove_playlists_for_user

from functions.plex_connection import plex_user_connection

from classes import PlexData

####### CODE HERE (Nothing to change) ############

def list_updater(plex):
    """ Runs main method to update all playlists and collections """
    plex_data = PlexData(plex)

    plex_data.display_shared_users()

    film_lists = []

    film_lists = film_lists + trakt_list_loop()
    film_lists = film_lists + imdb_list_loop()

    # Process Lists
    for filmlist in film_lists:
        filmlist.setup_playlist(plex_data)

if __name__ == "__main__":
    print("===================================================================")
    print("   Automated Playlist to Plex script   ")
    print("===================================================================\n")

    if (len(sys.argv) == 1 or sys.argv[1] not in [
            'test',
            'run',
            'imdb_ids',
            'show_users',
            'show_allowed',
            'remove_playlist',
            'remove_all_playlists',
            'discord_test'
        ]):
        print("""
Please use one of the following commands:
    run - Will start the normal process from your settings
    imdb_ids - needs url (in quotes probably) then type (custom,chart,search) to show list of imdb ids from url
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
        PLEX = plex_user_connection()
    except Exception: # pylint: disable=broad-except
        print("No Plex server found at: {base_url} or bad plex token code".format(
            base_url=global_vars.PLEX_URL
        ))
        input("press enter to exit")
        sys.exit()


    # run standard
    if sys.argv[1] == 'run':
        list_updater(PLEX)

    # check imdb list from url
    if sys.argv[1] == 'imdb_ids':
        if len(sys.argv) >= 3:
            IMDB_IDS, TITLE = get_imdb_info(sys.argv[2], sys.argv[3])
            print('title: {0}, count: {2} ids: {1}'.format(TITLE, IMDB_IDS, len(IMDB_IDS)))
        else:
            print("Please supply url then type")


    # display available users
    if sys.argv[1] == 'show_users':
        USERS = get_all_users(PLEX)
        print('{} shared users'.format(len(USERS)))
        for key, value in USERS.items():
            print('Username: {}'.format(key))

    # display allowed users based on settings
    if sys.argv[1] == 'show_allowed':
        USERS = get_user_tokens(PLEX)
        print('{} shared users'.format(len(USERS)))
        for key, value in USERS.items():
            print('Username: {}'.format(key))

    if sys.argv[1] == 'remove_playlist':
        if len(sys.argv) >= 3:
            print('removing playlist {}'.format(sys.argv[2]))
            PLEX_DATA = PlexData(PLEX)
            remove_shared_playlist(PLEX_DATA, sys.argv[2])
        else:
            print("Please supply a playlist name for the second command argument")

    if sys.argv[1] == 'remove_all_playlists':
        removing_film_lists = []
        removing_film_lists += trakt_list_loop()
        removing_film_lists += imdb_list_loop()

        remove_playlists_for_user(PLEX, removing_film_lists)

    if sys.argv[1] == 'discord_test':
        print("Testing sending to discord")
        print("using URL: {}".format(global_vars.DISCORD_URL))

        MESSAGE = {}
        FIRST_PART = {}
        FIRST_PART["title"] = "Playlists connected"
        MESSAGE['embeds'] = [FIRST_PART]
        JSON_DATA = json.dumps(MESSAGE)
        RES = requests.post(
            global_vars.DISCORD_URL,
            headers={"Content-Type":"application/json"},
            json=MESSAGE
        )
        if RES.status_code == 204:
            print("You should see a message in discord.")

    if sys.argv[1] == 'test':
        print("Testing")


    print("\n===================================================================")
    print("                               Done!                               ")
    print("===================================================================\n")

    log_timer()
