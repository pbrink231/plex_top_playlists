""" Methods to pull trakt data into Film Lists """
from urllib.request import Request, urlopen
import json
from classes import ListSource, FilmItem, FilmList, FilmDB, FilmType
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

    film_lists = []
    for runlist in global_vars.TRAKT_MOVIE_LISTS:
        kind = runlist.get("kind", 'playlist')
        show_summary = runlist.get("show_summary", True)
        title = runlist["title"]
        print("PULLING LIST - {0}: URL: {1} - TYPE: {2} - KIND: {3}".format(
            title,
            runlist["url"],
            runlist["type"],
            kind
        ))
        trakt_movie_data = request_trakt_list(runlist["url"], runlist["limit"])
        trakt_list_items = trakt_movie_list_items(trakt_movie_data, runlist["type"])

        film_lists.append(FilmList(ListSource.TRAKT, title, trakt_list_items, kind, show_summary))

    return film_lists


def trakt_show_list_loop():
    """ returns all film lists from the trakt shows api """
    if global_vars.TRAKT_API_KEY is None:
        print("No Trakt API key, skipping Trakt Show lists")
        return None
    
    print(f'count of trakt shows lists: {len(global_vars.TRAKT_SHOW_LISTS)}')

    film_lists = []
    for runlist in global_vars.TRAKT_SHOW_LISTS:
        kind = runlist.get("kind", 'playlist')
        show_summary = runlist.get("show_summary", True)
        title = runlist["title"]
        print("PULLING LIST - {0}: URL: {1} - TYPE: {2} - KIND: {3}".format(
            title,
            runlist["url"],
            runlist["type"],
            kind
        ))
        trakt_shows_data = request_trakt_list(runlist["url"], runlist["limit"])
        trakt_list_items = trakt_tv_list_items(trakt_shows_data, runlist["type"])

        film_lists.append(FilmList(ListSource.TRAKT, title, trakt_list_items, kind, show_summary))

    return film_lists

def trakt_user_list_loop():
    """ returns all film lists from the trakt shows api """
    if global_vars.TRAKT_API_KEY is None:
        print("No Trakt API key, skipping Trakt Show lists")
        return None

    print(f'count of trakt users lists: {len(global_vars.TRAKT_USERS_LISTS)}')

    film_lists = []
    for runlist in global_vars.TRAKT_USERS_LISTS:
        kind = runlist.get("kind", 'playlist')
        show_summary = runlist.get("show_summary", True)
        title = runlist["title"]
        print("PULLING LIST - {0}: URL: {1} - TYPE: {2} - KIND: {3}".format(
            title,
            runlist.get("url"),
            runlist.get("type"),
            kind
        ))
        trakt_shows_data = request_trakt_list(runlist["url"], runlist["limit"])
        trakt_list_items = trakt_user_list_items(trakt_shows_data)

        film_lists.append(FilmList(ListSource.TRAKT, title, trakt_list_items, kind, show_summary))

    return film_lists

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
    except Exception: # pylint: disable=broad-except
        print("Bad Trakt Code")
        return None

def trakt_tv_list_items(trakt_json, json_type):
    """ converts data to film items from trakt tv api endpoint """
    film_items = []
    if json_type == "watched":
        for show in trakt_json:
            film_items.append(FilmItem(
                str(show['show']['ids']['tvdb']),
                FilmDB.TVDB,
                FilmType.SHOW
            ))
    if json_type == "popular":
        for show in trakt_json:
            film_items.append(FilmItem(str(show['ids']['tvdb']), FilmDB.TVDB, FilmType.SHOW))
    return film_items

def trakt_movie_list_items(trakt_json, json_type):
    """ converts data to film items from trakt movie api endpoint """
    film_items = []
    if json_type == "watched":
        for movie in trakt_json:
            film_items.append(FilmItem(movie['movie']['ids']['imdb'], FilmDB.IMDB, FilmType.MOVIE))
    if json_type == "popular":
        for movie in trakt_json:
            film_items.append(FilmItem(movie['ids']['imdb'], FilmDB.IMDB, FilmType.MOVIE))
    return film_items

def trakt_user_list_items(trakt_json):
    """ converts data to film items from trakt user api endpoint """
    film_items = []
    for item in trakt_json:
        if item['type'] == 'movie':
            film_items.append(FilmItem(
                item['movie']['ids']['imdb'],
                FilmDB.IMDB,
                FilmType.MOVIE
            ))
        if item['type'] == 'show':
            film_items.append(FilmItem(
                str(item['show']['ids']['tvdb']),
                FilmDB.TVDB,
                FilmType.SHOW
            ))
        if item['type'] == 'season':
            film_items.append(FilmItem(
                str(item['season']['ids']['tvdb']),
                FilmDB.TVDB,
                FilmType.SHOW
            ))
        if item['type'] == 'episode':
            film_items.append(FilmItem(
                str(item['episode']['ids']['tvdb']),
                FilmDB.TVDB,
                FilmType.SHOW
            ))
    return film_items
