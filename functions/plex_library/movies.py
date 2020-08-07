""" Getting needed information plex libraries """
import re
import global_vars
from functions.logger import log_timer
from functions.plex_library.library_utils import show_dict_progress
import shelve
from tmdbv3api import TMDb, Movie

tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
tmdb_movie = Movie()

def get_library_movie_dictionary(plex):
    """ Returns a dictionary to easily reference movies by thier IMDB ID"""
    all_movies = get_library_movies(plex)

    print("Creating movie dictionary based on IMDB ID")
    return create_movie_id_dict(all_movies)


def get_library_movies(plex):
    """ Getting Movie libraries dictionary """
    # Get list of movies from the Plex server
    # split into array
    movie_libs = global_vars.MOVIE_LIBRARY_NAME.split(",")
    all_movies = []

    # loop movie lib array
    for lib in movie_libs:
        lib = lib.strip()
        print("Retrieving a list of movies from the '{library}' "
              "library in Plex...".format(library=lib))
        try:
            movie_library = plex.library.section(lib)
            new_movies = movie_library.all()
            all_movies = all_movies + new_movies
            print("Added {length} movies to your 'all movies' "
                  "list from the '{library}' library in Plex...".format(
                      library=lib,
                      length=len(new_movies)))
            log_timer()
        except Exception: # pylint: disable=broad-except
            print("The '{library}' library does not exist in Plex.".format(library=lib))

    print("Found {0} movies total in 'all movies' list from Plex...".format(
        len(all_movies)
    ))

    return all_movies


def create_movie_id_dict(movies):
    """ Creates a dictionary for easy searching by imdb ID """
    movie_id_dict = {}
    count = len(movies)
    cur = 1
    for movie in movies:
        movie_id_dict = append_movie_id_dict(movie, movie_id_dict)
        show_dict_progress(cur, count)
        cur += 1
    print("\ncached plex movies")
    return movie_id_dict

def append_movie_id_dict(movie, movie_id_dict):
    """ Adds movie to dictionary with imdb ID as key and movie as value """
    imdb_id = get_used_id(movie)
    if imdb_id is not None:
        movie_id_dict[imdb_id] = movie
    return movie_id_dict

def get_imdb_id(movie):
    """ grabs the imdb ID from the movie """
    try:
        # com.plexapp.agents.imdb://tt0137523?lang=en
        imdb_id = "tt" + re.search(r'tt(\d+)\?', movie.guid).group(1)
    except Exception: # pylint: disable=broad-except
        imdb_id = None
    return imdb_id

def get_used_id(movie):
    try:
        agent = re.search(r'com\.plexapp\.agents\.(.+)\:\/\/', movie.guid).group(1)
        if (agent == 'imdb'):
            # com.plexapp.agents.imdb://tt0137523?lang=en
            imdb_id = "tt" + re.search(r'tt(\d+)\?', movie.guid).group(1)
        if (agent == 'themoviedb'):
            # com.plexapp.agents.themoviedb://550?lang=en
            with shelve.open('tmdb_ids', 'c', writeback=True) as s:
                tmdb_id = re.search(r'\:\/\/(\d+)\?', movie.guid).group(1)
                if s.get(tmdb_id) == None:
                    s[tmdb_id] = tmdb_movie.external_ids(tmdb_id)["imdb_id"]
                imdb_id = s[tmdb_id]
    except Exception as e:
        print("{0}".format(e))
        imdb_id = None
    return imdb_id
