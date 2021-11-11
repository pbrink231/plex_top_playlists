""" Methods dealing with plex collections """
from classes.visibility import Visibility
from functions.plex_request import updateVisibility
import global_vars
from classes import FilmType

def add_library_items_to_collection(plex, title, items, sort, visibility):
    """ Adds plex items to a collection """

    ## Create collection
    library, collection = createCollection(plex, title, items)

    ## Sort Collection
    sortCollection(collection, items, sort)

    ## Update Mode (Default = Hide Collection and keep items visible in library)
    collection.modeUpdate('hide')
    collection.reload()

    ## Update Visibility
    updateVisibility(collection, visibility)

    ## Reload Library & Collection
    collection.reload()
    library.reload()

def createCollection(plex, title, items):

    ## TODO: Specific when reading lists what library its going to
    section = global_vars.MOVIE_LIBRARY_NAME
    if items[0].type != 'movie':
        section = global_vars.SHOW_LIBRARY_NAME

    library = plex.library.section(section)
    collection_list = [x.title for x in library.collections()] ## All collections in library
    collection = None

    ## Reuse collection and add new items
    if title in collection_list: ## Check if collection exists
        collection = library.collection(title)
        collection.removeItems(collection.items()) ## Remove all items in collection
        collection.reload()
        collection.addItems(items) ## Add new items
        collection.reload()

    ## Create new non-smart collection and new items
    else:
        library.createCollection(title, items=items, smart=False) ## Create stupid collection
        library.reload()
        collection = library.collection(title)

    return library, collection

def sortCollection(collection, items, sort):

    if sort == 'custom':
        ## Order collection by order of list
        orderByList(collection, items)
    else: ## 'alpha' or 'release'
        ## Update collection sort order
        collection.sortUpdate(sort)
        collection.reload()  

def orderByList(collection, items):

    ## Order collection based on imported list order
    collection.reload()

    # Move first item to correct place
    collection.moveItem(items[0])
    collection.reload()

    # Move remaining items to correct place
    for i in range(len(items)-1):
        collection.moveItem(items[i+1], items[i])
        collection.reload()
