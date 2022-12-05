""" Methods to pull trakt data into Film Lists """
from urllib.request import Request, urlopen
import json

from classes import ListSource, FilmItem, FilmList, FilmDB, FilmType, visibility
from classes.visibility import Visibility
from utils.logger import log_output
import global_vars

def trakt_list_loop():
    """ Returns all trakt film lists """
    all_trakt_film_lists = []
    all_trakt_film_lists += trakt_movie_list_loop()
    all_trakt_film_lists += trakt_show_list_loop()
    all_trakt_film_lists += trakt_user_list_loop()
    return all_trakt_film_lists

def trakt_movie_list_loop():
    """ returns all film lists from the trakt movies api """
    if global_vars.TRAKT_API_KEY is None:
        print("No Trakt API key, skipping Trakt movie lists")
        return None

    print(f'count of trakt movies lists: {len(global_vars.TRAKT_MOVIE_LISTS)}')

    return get_film_lists(global_vars.TRAKT_MOVIE_LISTS, 'movie')

def trakt_show_list_loop():
    """ returns all film lists from the trakt shows api """
    if global_vars.TRAKT_API_KEY is None:
        print("No Trakt API key, skipping Trakt Show lists")
        return None
    
    print(f'count of trakt shows lists: {len(global_vars.TRAKT_SHOW_LISTS)}')

    return get_film_lists(global_vars.TRAKT_SHOW_LISTS, 'show')

def trakt_user_list_loop():
    """ returns all film lists from the trakt shows api """
    if global_vars.TRAKT_API_KEY is None:
        print("No Trakt API key, skipping Trakt Show lists")
        return None

    print(f'count of trakt users lists: {len(global_vars.TRAKT_USERS_LISTS)}')

    return get_film_lists(global_vars.TRAKT_USERS_LISTS)

def get_film_lists(trakt_lists, response_base_type=None):
    """ Loops trakt settings lists and returns setup film lists """
    film_lists = []
    for runlist in trakt_lists:
        kind = runlist.get("kind", 'playlist')
        sort = runlist.get("sort", 'custom')
        show_summary = runlist.get("show_summary", True)
        title = runlist["title"]
        visibility = runlist.get('visibility',{})
        if type(visibility) == str and visibility == "all":
            visibility = Visibility(1, 1, 1)
        else:
            visibility = Visibility(**visibility)
        print("PULLING LIST - {0}: URL: {1} - TYPE: {2} - KIND: {3} - SORT: {4} - VISIBILITY: {5}".format(
            title,
            runlist.get("url"),
            runlist.get("type"),
            kind,
            sort,
            visibility.to_string()
        ))
        item_base = None
        # Popular lists are based on type and returned JSON is different
        # Watched returns normal json
        if runlist.get("type") == "popular":
            if response_base_type:
                item_base = response_base_type
            else:
                raise Exception("Missing required base for popular list")

        trakt_data = request_trakt_list(runlist["url"], runlist["limit"])
        if trakt_data is None:
            print(f"WARNING: SKIPPING LIST, No trakt data for list {title}")
            return []

        trakt_film_items = get_film_items(trakt_data, item_base)

        film_lists.append(FilmList(ListSource.TRAKT, title, trakt_film_items, visibility, kind, show_summary, sort))

    return film_lists

def get_film_items(trakt_json, item_base):
    """ converts data to film items from trakt user api endpoint """
    log_output(f"trakt json {trakt_json}", 3)
    film_items = []
    for item in trakt_json:
        film_items.append(get_film_item(item, item_base))

    return film_items

def get_film_item(item, item_base):
    """ Grabs the correct information and returns a Film Item """
    log_output(f"trakt user item: {item}", 3)
    if item_base == 'movie':
        return FilmItem(
            film_id=item['ids']['imdb'],
            film_db=FilmDB.IMDB,
            film_type=FilmType.MOVIE,
            title=item['title']
        )
    if item_base == 'show':
        return FilmItem(
            film_id=item['ids']['tvdb'],
            film_db=FilmDB.TVDB,
            film_type=FilmType.SHOW,
            title=item['title']
        )
    if item.get('type') == 'movie' or item.get('movie'):
        return FilmItem(
            film_id=item['movie']['ids']['imdb'],
            film_db=FilmDB.IMDB,
            film_type=FilmType.MOVIE,
            title=item['movie']['title']
        )
    if item.get('type') == 'show' or item.get('show'):
        season_num = None
        episode_num = None
        if item.get('episode'):
            season_num = item['episode']['season']
            episode_num = item['episode']['number']

        if item.get('season'):
            season_num = item['season']['number']

        return FilmItem(
            film_id=str(item['show']['ids']['tvdb']),
            film_db=FilmDB.TVDB,
            film_type=FilmType.SHOW,
            title=item['show']['title'],
            season_num=season_num,
            episode_num=episode_num
        )


def request_trakt_list(url, limit):
    """ retrieves data from trakt using the api """
    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version': '2',
        'trakt-api-key': global_vars.TRAKT_API_KEY
    }
    request = Request('{}?page=1&limit={}'.format(url, limit), headers=headers)
    try:
        response = urlopen(request)
        trakt_data = json.load(response)
        return trakt_data
    except Exception as ex: # pylint: disable=broad-except
        print(f"ERROR: Bad Trakt Request: {ex}")
        return None