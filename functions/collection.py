""" Methods dealing with plex collections """

def add_library_items_to_collection(title, items):
    """ Adds plex items to a collection """
    for library_item in items:
        library_item.addCollection(title)
