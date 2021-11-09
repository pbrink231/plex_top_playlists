""" Methods dealing with plex collections """
import global_vars
from classes import FilmType

def add_library_items_to_collection(title, items, plex):
    """ Adds plex items to a collection """

    ## Create/recreate the collection
    print([x for x in items])
    
    section = global_vars.MOVIE_LIBRARY_NAME
    if items[0].type != 'movie':
        section = global_vars.SHOW_LIBRARY_NAME

    library = plex.library.section(section) ## library short form
    libraryCollections = [x.title for x in library.collections()] ## All movie collections
    collection = None

    if title in libraryCollections: ## Check if collection exists
        collection = library.collection(title)
        collection.removeItems(collection.items()) ## Remove all items in collection
        collection.reload()
        collection.addItems(items) ## Add new items
        collection.reload()
    else:
        library.createCollection(title, items=items, smart=False) ## Create stupid collection
        library.reload()
        collection = library.collection(title)
        collection.sortUpdate('custom') ## Set sort order
        collection.reload()

    ## Correctly order collection

    # Move first item to correct place
    collection.moveItem(items[0])
    collection.reload()

    # Move remaining items to correct place
    for i in range(len(items)-1):
        collection.moveItem(items[i+1], items[i])
        collection.reload()
