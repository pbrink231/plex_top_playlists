""" IMDB lists translated into FilmLists """
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import List
from lxml import html
import requests

from classes import FilmList, FilmItem, FilmDB, FilmType, ListSource
from classes.visibility import Visibility
import global_vars

def imdb_list_loop() -> List[FilmList]:
    """ Loops IMDB lists and returns FilmLists """
    print('count of imdb lists: {}'.format(len(global_vars.IMDB_LISTS)))
    film_lists = []
    for runlist in global_vars.IMDB_LISTS:
        film_list = get_imdb_film_list(runlist)

        if film_list:
            film_lists.append(film_list)

    return film_lists

def get_imdb_film_list(runlist):
    """ Gets a FilmList from and IMDB list """
    using_url = runlist["url"]
    list_type = runlist["type"]
    imdb_ids, title = get_imdb_info(using_url, list_type)
    sort = runlist.get("sort", 'custom')
    visibility = runlist.get('visibility',{})
    if type(visibility) == str and visibility == "all":
        visibility = Visibility(1, 1, 1)
    else:
        visibility = Visibility(**visibility)

    if runlist["title"]:
        title = runlist["title"] # imdb_list_name(tree, runlist["type"])

    if not title:
        print("SKIPPING LIST because no title found")
        return None

    film_items = []
    for imdb_id in imdb_ids:
        film_items.append(FilmItem(imdb_id, FilmDB.IMDB, FilmType.MOVIE))

    kind = runlist.get("kind", 'playlist')
    show_summary = runlist.get("show_summary", True)

    return FilmList(ListSource.IMDB, title, film_items, visibility, kind, show_summary, sort)

def get_imdb_info(using_url, list_type):
    """ Gets the imdb_ids and title from a imdb url with type """
    title = None
    imdb_ids = []
    while True:
        print("getting imdb ids from url: {0}".format(using_url))
        page = requests.get(using_url)
        tree = html.fromstring(page.content)
        new_ids = imdb_list_ids(tree, list_type)
        imdb_ids += new_ids

        if title is None:
            title = imdb_list_name(tree, list_type)

        is_next = tree.xpath("//a[@class='flat-button lister-page-next next-page']")
        if is_next:
            parsed = urlparse(using_url)
            url_parts = list(parsed)
            query = dict(parse_qsl(url_parts[4]))
            cur_page = query.get("page", 1)
            next_page = int(cur_page) + 1
            params = {'page': next_page}
            query.update(params)
            url_parts[4] = urlencode(query)
            using_url = urlunparse(url_parts)
        else:
            break

    return imdb_ids, title

def imdb_list_name(tree, list_type):
    """ Gets the imdb list name from the html """
    if list_type == "chart":
        return tree.xpath("//h1[contains(@class, 'header')]")[0].text.strip()
    if list_type == "search":
        return tree.xpath("//h1[contains(@class, 'header')]")[0].text.strip()
    if list_type == "custom":
        return tree.xpath("//h1[contains(@class, 'header list-name')]")[0].text.strip()
    return

def imdb_list_ids(tree, list_type):
    """ Gets teh imdb id from the html """
    if list_type == "chart":
        return tree.xpath("//table[contains(@class, 'chart')]//td[@class='ratingColumn']/div//@data-titleid")
    if list_type == "search":
        return tree.xpath("//img[@class='loadlate']/@data-tconst")
    if list_type == "custom":
        return tree.xpath("//div[contains(@class, 'lister-item-image ribbonize')]/@data-tconst")
    return
