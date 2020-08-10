""" Enums used in app """
# Python code to demonstrate enumerations
# iterations and hashing
# importing enum for enumerations
from enum import Enum

class FilmListKind(Enum):
    """ Different kinds of lists """
    PLAYLIST = 1
    COLLECTION = 2

# creating enumerations using class
class FilmDB(Enum):
    """ Film Database to use for lookup in the app """
    IMDB = 1
    TVDB = 2

# creating enumerations using class
class FilmType(Enum):
    """ Film types possible """
    MOVIE = 1
    SHOW = 2
    SEASON = 3
    EPISODE = 4

class ListSource(Enum):
    """ Sources to pull lists from """
    IMDB = 1
    TRAKT = 2
