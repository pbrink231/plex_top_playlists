""" Methods to work with plex playlists """
import os
import sys

from functions.plex_connection import plex_user_connection
from functions.sources.all import get_all_film_lists
import global_vars

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def add_playlist_to_plex_users(plex, shared_users_token, title, items):
    """ Adds a playlist to all shared users """
    if not items:
        print("{}: list EMPTY so will only be REMOVED and not created".format(title))

    # update my list
    create_playlists(plex, title, items)
    print("{}: Playlist made for primary user".format(title))

    # update list for shared users
    if global_vars.SYNC_WITH_SHARED_USERS:
        for user in shared_users_token:
            user_token = shared_users_token[user]
            user_plex = plex_user_connection(user_token)
            create_playlists(user_plex, title, items)
            print("{}: playlist made for user {}".format(title, user))

    else:
        print("Skipping adding to shared users")

def create_playlists(plex, title, items):
    """ creates a playlist for the plex user """
    try:
        remove_playlist(plex, title)
        if items:
            plex.createPlaylist(title, items)
    except Exception: # pylint: disable=broad-except
        print(f"""
        ERROR trying to create playlist '{title}'
        The number of movies/shows in the list provided was {len(items)}
        """)


def remove_shared_playlist(plex, shared_users_token, title: str):
    """ removes playlists for main plex user and all shared users """
    # update my list
    print("{}: removing playlist for script user".format(title))
    remove_playlist(plex, title)

    # update list for shared users
    if global_vars.SYNC_WITH_SHARED_USERS:
        for user in shared_users_token:
            print("{0}: removing playlist for user {1}".format(
                title,
                user
            ))
            user_token = shared_users_token[user]
            user_plex = plex_user_connection(user_token)
            remove_playlist(user_plex, title)
    else:
        print("Skipping removal from shared users")

def remove_all_playlists_for_user(plex):
    """ removes all of a users playlists on the Plex Server """
    all_film_lists = get_all_film_lists()

    for film_list in all_film_lists:
        print(f"Removing playlists '{film_list.title}'")
        remove_playlist(plex, film_list.title)



def remove_playlist(plex, title):
    """ deletes a playlist for the plex user """
    for playlist in plex.playlists():
        if playlist.title == title:
            try:
                playlist.delete()
            except Exception: # pylint: disable=broad-except
                print("ERROR - cannot delete playlist: {}".format(title))

    return None
