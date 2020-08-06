""" Plex connection methods """
from plexapi.server import PlexServer
import global_vars

def plex_user_connection(user_token=global_vars.PLEX_TOKEN):
    """ returns a connection to plex for a user """
    return PlexServer(
        baseurl=global_vars.PLEX_URL,
        token=user_token,
        timeout=global_vars.PLEX_TIMEOUT
    )
