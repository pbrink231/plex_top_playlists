""" Methods dealing with plex collections """
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
        collection = library.collection(title)

    myCollection.sortUpdate(sort) ## Set sort order
    myCollection.reload()

    ## Stop here if no custom order is wanted
    if sort != 'custom':
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
