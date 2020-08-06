""" Combining all data from the different sources """

from typing import List
from classes import FilmList
from trakt import trakt_list_loop
from imdb import imdb_list_loop

def get_all_film_lists() -> List[FilmList]:
    """ Returns all Film Lists from the different sources """
    all_trakt_film_lists = []
    all_trakt_film_lists += trakt_list_loop()
    all_trakt_film_lists += imdb_list_loop()
    return all_trakt_film_lists
