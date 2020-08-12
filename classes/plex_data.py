""" Overall plex data cacher to easily search movies and shows
by IMDB ID and TVDB ID """
from functions.users import get_user_tokens
from functions.plex_library.movies import get_library_movie_dictionary
from functions.plex_library.shows import get_library_show_dictionary

from utils.logger import log_output

from classes import FilmType, FilmDB

class PlexData:
    """ Class to hold cached plex data for testing against lists """
    def __init__(self, plex):
        self.plex = plex
        self.shared_users_token = get_user_tokens(plex)
        self.all_movie_id_dict = get_library_movie_dictionary(plex)
        self.all_show_id_dict = get_library_show_dictionary(plex)

    def display_shared_users(self):
        """ Show users being used for all lists """
        log_output("shared users list: {}".format(self.shared_users_token), 1)

    def get_matching_item(self, film_item):
        """ Grabs the matched library item with the film item """
        found_item = None
        if film_item.film_type == FilmType.MOVIE:
            return self.all_movie_id_dict.get(film_item.film_id)
        else:
            return self.get_show_episode(film_item)

        raise Exception(f"Film DB Unknown {film_item.film_db}")

    def get_show_episode(self, film_item):
        """ Returns the corresponding episode """
        found_show = self.all_show_id_dict.get(film_item.film_id)

        if not found_show:
            return found_show

        if film_item.film_type == FilmType.SHOW:
            # Return last episode
            return found_show.episodes()[-1]

        if film_item.film_type == FilmType.SEASON:
            # Return first episode in season
            # TO DO FIX
            return found_show.episodes()[-1]

        if film_item.film_type == FilmType.EPISODE:
            # Return specific episode
            # TO DO FIX
            return found_show.episodes()[-1]

        raise Exception(f"Film List Type Unknown {film_item.film_type}")
