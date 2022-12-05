""" Methods to get show data from plex """
import global_vars

from functions.plex_library.library_utils import show_dict_progress

from utils.logger import log_timer


def get_library_show_dictionary(plex):
    """ Returns a dictionary for all shows by ID for easier searching """
    all_shows = get_library_shows(plex)

    print("Creating show dictionary based on TVDB ID")
    return create_show_id_dict(all_shows)



def get_library_shows(plex):
    """ Gets a list of shows from plex libraries """
    # Get list of shows from the Plex server
    # split into array
    show_libs = global_vars.SHOW_LIBRARY_NAME.split(",")
    all_shows = []
    # loop movie lib array
    for lib in show_libs:
        lib = lib.strip()
        print("Retrieving a list of shows from the '{library}' "
              "library in Plex...".format(library=lib))
        try:
            show_library = plex.library.section(lib)
            new_shows = show_library.all()
            all_shows = all_shows + new_shows
            print("Added {length} shows to your 'all shows' list from the '{library}' "
                  "library in Plex...".format(library=lib, length=len(new_shows)))
            log_timer()
        except Exception: # pylint: disable=broad-except
            print("The '{library}' library does not exist in Plex.".format(library=lib))

    print("Found {0} show total in 'all shows' list from Plex...".format(
        len(all_shows)
    ))

    return all_shows

def create_show_id_dict(shows):
    """ Creates a dictionary for easy searching by tvdb ID """
    show_id_dict = {}
    count = len(shows)
    cur = 1
    for show in shows:
        show_id_dict = append_show_id_dict(show, show_id_dict)
        show_dict_progress(cur, count)
        cur += 1
    print(f"\nFinished Creating Show Dictionary")
    
    return show_id_dict

def append_show_id_dict(show, show_id_dict):
    """ Adds show to dictionary with tvdb ID as key and show as value """
    tvdb_id = get_tvdb_id(show)
    if tvdb_id is not None:
        show_id_dict[tvdb_id] = show
    return show_id_dict

def get_tvdb_id(show):
    """ Gets the tvdb ID from the show """
    tvdb_id = None
    last_episode = show.episodes()[-1]

    for show_guid in show.guids:
         if show_guid.id != "" and 'tvdb://' in show_guid.id:
            tvdb_id = show_guid.id.split('tvdb://')[1].split('?')[0].split('/')[0]

    return tvdb_id
