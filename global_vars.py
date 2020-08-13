""" Container for all globals used in this app """
import configparser
import os
import sys
import json
import time

from utils.logger import log_output

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'settings.ini'
)

if not os.path.isfile(CONFIG_PATH):
    print("Please create a settings.ini file in the same folder as plex_playlist_update.py")
    sys.exit("No settings.ini file")

CONFIG = configparser.SafeConfigParser()
CONFIG.read(CONFIG_PATH)

global START_TIME
START_TIME = time.time()

global TEST
TEST = 'hello'

# Plex information
global PLEX_URL
PLEX_URL = CONFIG.get('Plex', 'plex-host', fallback=None)
global PLEX_TOKEN
PLEX_TOKEN = CONFIG.get('Plex', 'plex-token', fallback=None)
global MOVIE_LIBRARY_NAME
MOVIE_LIBRARY_NAME = CONFIG.get('Plex', 'movie-library', fallback=None)
global SHOW_LIBRARY_NAME
SHOW_LIBRARY_NAME = CONFIG.get('Plex', 'tv-library', fallback=None)
global SYNC_WITH_SHARED_USERS
SYNC_WITH_SHARED_USERS = CONFIG.getboolean('Plex', 'shared', fallback=False)
global ALLOW_SYNCED_USERS
ALLOW_SYNCED_USERS = json.loads(CONFIG.get('Plex', 'users', fallback=[]))
global NOT_ALLOW_SYNCED_USERS
NOT_ALLOW_SYNCED_USERS = json.loads(CONFIG.get('Plex', 'not_users', fallback=[]))

# Sonarr globals
global SONARR_USE
SONARR_USE = CONFIG.getboolean('Sonarr', 'sonarr-add-missing', fallback=False)
global SONARR_URL
SONARR_URL = CONFIG.get('Sonarr', 'sonarr-url', fallback=None)
global SONARR_TOKEN
SONARR_TOKEN = CONFIG.get('Sonarr', 'sonarr-token', fallback=None)
global SONARR_PROFILE_ID
SONARR_PROFILE_ID = CONFIG.get('Sonarr', 'sonarr-profile-id', fallback=None)
global SONARR_PATH
SONARR_PATH = CONFIG.get('Sonarr', 'sonarr-path', fallback=None)

global VERBOSE
try:
    VERBOSE = int(CONFIG.get('Plex', 'verbose'))
except Exception: # pylint: disable=broad-except
    VERBOSE = 0

global PLEX_TIMEOUT
try:
    PLEX_TIMEOUT = int(CONFIG.get('Plex', 'timeout'))
except Exception: # pylint: disable=broad-except
    PLEX_TIMEOUT = 300

global SHOW_MISSING
try:
    SHOW_MISSING = CONFIG.getboolean('Plex', 'show_missing')
except Exception: # pylint: disable=broad-except
    SHOW_MISSING = False

global MISSING_COLUMNS
try:
    MISSING_COLUMNS = int(CONFIG.get('Plex', 'missing_columns'))
except Exception: # pylint: disable=broad-except
    MISSING_COLUMNS = 4

global SHOW_MISSING_TITLES
try:
    SHOW_MISSING_TITLES = CONFIG.getboolean('Plex', 'show_missing_titles')
except Exception: # pylint: disable=broad-except
    SHOW_MISSING_TITLES = False

try:
    TMDB_API_KEY = config.get('TMDb', 'api-key')
except:
    TMDB_API_KEY = None

global TRAKT_API_KEY
try:
    TRAKT_API_KEY = CONFIG.get('Trakt', 'api-key')
except Exception: # pylint: disable=broad-except
    TRAKT_API_KEY = None

global TRAKT_MOVIE_LISTS
try:
    TRAKT_MOVIE_LISTS = json.loads(CONFIG.get('Trakt', 'trakt-movie-list'))
except Exception as ex: # pylint: disable=broad-except
    print(f"SKIPPING SETTINGS LIST: Problem with trakt-movie-list, {ex}")
    log_output(sys.exc_info(), 3)
    TRAKT_MOVIE_LISTS = []

global TRAKT_SHOW_LISTS
try:
    TRAKT_SHOW_LISTS = json.loads(CONFIG.get('Trakt', 'trakt-tv-list'))
except Exception as ex: # pylint: disable=broad-except
    print(f"SKIPPING SETTINGS LIST: Problem with trakt-show-list, {ex}")
    log_output(sys.exc_info(), 3)
    TRAKT_SHOW_LISTS = []

global TRAKT_USERS_LISTS
try:
    TRAKT_USERS_LISTS = json.loads(CONFIG.get('Trakt', 'trakt-users-list'))
except Exception as ex: # pylint: disable=broad-except
    print(f"SKIPPING SETTINGS LIST: Problem with trakt-user-list, {ex}")
    log_output(sys.exc_info(), 3)
    TRAKT_USERS_LISTS = []

global IMDB_LISTS
try:
    IMDB_LISTS = json.loads(CONFIG.get('IMDb', 'imdb-lists'))
except Exception as ex: # pylint: disable=broad-except
    print(f"SKIPPING SETTINGS LIST: Problem with imdb-lists, {ex}")
    log_output(sys.exc_info(), 3)
    IMDB_LISTS = []

global DISCORD_URL
try:
    DISCORD_URL = CONFIG.get('Discord', 'webhook_url')
except Exception: # pylint: disable=broad-except
    DISCORD_URL = None
