""" Getting needed information plex libraries """
import re
import shelve
from tmdbv3api import TMDb, Movie
import global_vars

from functions.plex_library.library_utils import show_dict_progress

from utils.logger import log_timer



tmdb = TMDb()
tmdb.api_key = global_vars.TMDB_API_KEY
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
    print(f"\nFinished Creating Movie Dictionary")
    return movie_id_dict

def append_movie_id_dict(movie, movie_id_dict):
    """ Adds movie to dictionary with imdb ID as key and movie as value """
    imdb_id = get_imdb_id(movie)
    if imdb_id is not None:
        movie_id_dict[imdb_id] = movie
    return movie_id_dict

def get_imdb_id(movie):
    """Gets the IMDB based on the agent used
    
    Some Guid examples
    local://36071
    com.plexapp.agents.imdb://tt0137523?lang=en
    com.plexapp.agents.themoviedb://550?lang=en
    plex://movie/5d776a8b9ab544002150043a
    """
    try:
        movie_reg = re.search(r'(?:plex://|com\.plexapp\.agents\.|)(.+?)(?:\:\/\/|\/)(.+?)(?:\?|$)', movie.guid)
        agent = movie_reg.group(1)
        movie_id = movie_reg.group(2)
        if agent == 'imdb':
            # com.plexapp.agents.imdb://tt0137523?lang=en
            return movie_id  # "tt" + re.search(r'tt(\d+)\?', movie.guid).group(1)
        if agent == 'themoviedb':
            # com.plexapp.agents.themoviedb://550?lang=en
            if not global_vars.TMDB_API_KEY:
                print(f"WARNING: Skipping, No TMDB API key: {movie.title}")
                return None

            with shelve.open('tmdb_ids', 'c', writeback=True) as s_db:
                tmdb_id = movie_id
                if s_db.get(tmdb_id) is None:
                    s_db[tmdb_id] = tmdb_movie.external_ids(tmdb_id)["imdb_id"]
                imdb_id = s_db[tmdb_id]
                return imdb_id
        if agent == 'movie':
            # plex://movie/5d776a8b9ab544002150043a
            # NEW AGENT, No external IDs available yet
            x_imdb_id = None
            for guid in movie.guids:
                if "imdb" in guid.id:
                    x_imdb_id = guid.id.replace('imdb://','')
            #print(f"NOTICE: Using new agent, let's hope this works: {movie.title}")

            return x_imdb_id
        
        if agent == 'local':
            print(f"WARNING: Skipping movie, using local agent: {movie.title}")
            return None

    except Exception as ex: # pylint: disable=broad-except
        print(f"IMDB ID ERROR: {movie.title}, {movie.guid}, {ex}")
        return None
