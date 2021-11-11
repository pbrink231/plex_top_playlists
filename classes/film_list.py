""" A list of different movies, shows, seasons or episodes. """
from typing import List
from classes.visibility import Visibility
import global_vars
from classes import ListSource, FilmListKind
from functions.playlists import add_playlist_to_plex_users
from functions.collection import add_library_items_to_collection
from functions.discord import send_simple_message

class FilmList(object):
    """__init__() functions as the class constructor"""
    def __init__(self, source, title: str, list_items, visibility: Visibility, kind: str = "playlist", show_summary: bool = True, sort: str = "custom"):
        self.list_source = source # ListSource
        self.title = title
        self.show_summary = show_summary
        self.list_items = list_items
        self.matched_library_items = []
        self.unmatched_film_items = []
        self.sort = sort
        self.visibility = visibility

        # Setup Kind correclty
        film_kind = FilmListKind[kind.upper()]
        if not film_kind:
            raise Exception(f"Film List Kind Unknown {kind}")

        self.kind = film_kind

    def setup_playlist(self, plex_data):
        """ Match lists with plex data """
        if self.list_items is None or not self.list_items:
            print(f"WARNING: {self.title} is empty so skipping")
            return

        print("{0}: finding matching movies for playlist with count {1}".format(
            self.title,
            len(self.list_items)
        ))

        self.match_items(plex_data)
        self.update_plex(plex_data)

        self.found_info()
        self.missing_info_print()
        self.missing_info_discord()

    def start_text(self):
        """ Text showing information before process start """
        print("{0}: STARTING - SOURCE: {2} - KIND: {1}".format(
            self.title,
            self.kind,
            self.list_source.name
        ))

    def match_items(self, plex_data):
        """ Will Process the film list and create/add any items to the playlist/collection """
        matched_library_items = []
        unmatched_film_items = []
        for film_item in self.list_items:
            library_item = plex_data.get_matching_item(film_item)
            if library_item:
                matched_library_items.append(library_item)
            else:
                unmatched_film_items.append(film_item)

        self.matched_library_items = matched_library_items
        self.unmatched_film_items = unmatched_film_items

    def update_plex(self, plex_data):
        """ Updates plex collection or playlist based on this list """
        if self.kind == FilmListKind.COLLECTION:
            # Update plex with playlist
            add_library_items_to_collection(plex_data.plex, self.title, self.matched_library_items, self.sort, self.visibility)
            return

        if self.kind == FilmListKind.PLAYLIST:
            # Update plex adding items to the collection
            add_playlist_to_plex_users(
                plex_data.plex,
                plex_data.shared_users_token,
                self.title,
                self.matched_library_items
            )
            return


        raise Exception(f"Film List Kind Unknown {self.kind}")

    def add_library_items_to_collection(self):
        """ Adds all film items to a collection with list title """
        for library_item in self.matched_library_items:
            library_item.addCollection(self.title)

    def found_info(self) -> str:
        """ Returns summary information for matches in text """
        text = """
        {match_lib_items_ct} of {items_ct} found in list:
            {playlist_name}
        MISSING: {miss_items_ct}""".format(
            playlist_name=self.title,
            items_ct=len(self.list_items),
            match_lib_items_ct=len(self.matched_library_items),
            miss_items_ct=len(self.unmatched_film_items),
        )

        return text

    def missing_info(self) -> str:
        """ Text display of list stats with missing info """
        id_list = ""
        list_length = len(self.unmatched_film_items)
        for i in range(list_length):
            film_item = self.unmatched_film_items[i]
            id_list += film_item.display()
            if i != 0 and i != list_length and (not (i + 1) % 4):
                id_list += '\n'
            elif i != list_length:
                id_list += '  |  '

        text = self.found_info() + '\n' + f"{id_list}"

        return text

    def missing_info_print(self):
        """Text for showing missing info"""
        if not global_vars.SHOW_MISSING or not self.show_summary:
            # skip showing missing_info
            return None

        print(self.missing_info())

    def missing_info_discord(self):
        """Send information to discord"""
        if not global_vars.DISCORD_URL or not self.show_summary:
            # Skip sending to discord
            return None

        send_simple_message(self.title, self.missing_info())
