""" Class declaration for Film Item """
import global_vars
from classes import FilmDB

import apps.sonarr as sonarr

class FilmItem:
    """ An Item for Film List """
    def __init__(self, film_id, film_db, film_type, title=None, season_num=None, episode_num=None):
        self.film_id = film_id
        self.film_db = film_db # imdb, tvdb
        self.film_type = film_type # movie, show, episode
        self.film_title = title # For displaying when cannot find in Plex
        self.season_num = season_num
        self.episode_num = episode_num

    def display(self) -> str:
        """ display text for film item """
        title_info = ""
        if global_vars.SHOW_MISSING_TITLES:
            title_info = f": {self.film_title}" if self.film_title else ""

        return f"{self.film_db.name}: {self.film_id}" + title_info

    def send_to_app(self):
        if self.film_db == FilmDB.TVDB and global_vars.SONARR_USE:
            sonarr.add_series(self.film_id)


