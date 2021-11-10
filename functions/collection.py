""" Methods dealing with plex collections """
from functions.plex_request import update_visibility
import global_vars
from classes import FilmType

def add_library_items_to_collection(title, items, sort, plex):
    """ Adds plex items to a collection """

    ## Create/recreate the collection
    # print([x for x in items])
    
    section = global_vars.MOVIE_LIBRARY_NAME
    if items[0].type != 'movie':
        section = global_vars.SHOW_LIBRARY_NAME

    library = plex.library.section(section) ## library short form
    libraryCollections = [x.title for x in library.collections()] ## All movie collections
    myCollection = None

    if title in libraryCollections: ## Check if myCollection exists
        myCollection = library.collection(title)
        myCollection.removeItems(myCollection.items()) ## Remove all items in collection
        myCollection.reload()
        myCollection.addItems(items) ## Add new items
        myCollection.reload()
    else:
        library.createCollection(title, items=items, smart=False) ## Create stupid collection
        library.reload()
        myCollection = library.collection(title)

    myCollection.sortUpdate(sort) ## Set sort order
    myCollection.reload()

    ## Stop here if no custom order is wanted
    if sort != 'custom':
        update_visibility(plex, section, title, 1, 1, 1)
        return

    ## Order collection based on imported list order

    # Move first item to correct place
    myCollection.moveItem(items[0])
    myCollection.reload()

    # Move remaining items to correct place
    for i in range(len(items)-1):
        myCollection.moveItem(items[i+1], items[i])
        myCollection.reload()

    myCollection.sortUpdate(sort) ## Set sort order
    myCollection.reload()

    update_visibility(plex, section, title, 1, 1, 1)

template = {
    'promotedToRecommended':1,
    'promotedToOwnHome':1,
    'promotedToSharedHome':1
    }

class Visibility:

    def __init__(self, promotedToRecommended=-1, promotedToOwnHome=-1, promotedToSharedHome=-1):
        
        if promotedToRecommended == -1:
            self.promotedToRecommended = promotedToRecommended
        else:
            self.promotedToRecommended = 1 if promotedToRecommended else 0

        if promotedToOwnHome == -1:
            self.promotedToOwnHome = promotedToOwnHome
        else:
            self.promotedToOwnHome = 1 if promotedToOwnHome else 0

        if promotedToSharedHome == -1:
            self.promotedToSharedHome = promotedToSharedHome
        else:
            self.promotedToSharedHome = 1 if promotedToSharedHome else 0

    def to_dict(self):

        ret_val = {}

        if self.promotedToRecommended != -1:
            ret_val['promotedToRecommended'] = self.promotedToRecommended

        if self.promotedToOwnHome != -1:
            ret_val['promotedToOwnHome'] = self.promotedToOwnHome

        if self.promotedToSharedHome != -1:
            ret_val['promotedToSharedHome'] = self.promotedToSharedHome

        return ret_val

    @staticmethod
    def keys():
        return ['promotedToRecommended', 'promotedToOwnHome', 'promotedToSharedHome']