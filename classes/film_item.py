""" Class declaration for Film Item """

class FilmItem:
    """ An Item for Film List """
    def __init__(self, film_id, film_db, film_type, film_options=None):
        self.film_id = film_id
        self.film_db = film_db # imdb, tvdb
        self.film_type = film_type # movie, show, episode

        # Additional options
        # TO DO
        if film_options:
            self.film_title = film_options.title # For displaying when cannot find in Plex
            self.film_year = film_options.year # For displaying when cannot find in Plex
            self.film_season = film_options.film_season # Used if a specific season is selected
            self.film_episode = film_options.film_episode # Used if a specific episode is selected

    def display(self) -> str:
        """ display text for film item """
        return f"{self.film_db.name}: {self.film_id}"
