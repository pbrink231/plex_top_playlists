""" Class declaration for Film Item """

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
        return f"{self.film_db.name}: {self.film_id}"
