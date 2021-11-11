
import json
import requests
from classes.visibility import Visibility

import global_vars
plexURLs = {
    'manageLibrary': '/hubs/sections/{library}/manage',
}

def identifier(collection):

    data = plex_get(
        plexURLs['manageLibrary'].format(library=collection.librarySectionID),
        {'metadataItemId': collection.ratingKey}
    )

    if 'MediaContainer' in data.keys() and 'Hub' in data['MediaContainer'].keys():
        
        return data['MediaContainer']['Hub'][0]['identifier']

    return None ## Returning None means the collection is currently has no visibility options set

def moveCollection(collection, after = None):
    """Move a collection to a new position in the library

    Parameters
    ----------
    collection : obj
        title of collection to be moved
    after : obj, optional
        title of collection to move the specified collection after, by default None
    """

    collection_id = identifier(collection)
    after_id = after
    if after:
        after_id = identifier(after)

    if collection_id:
        return plex_put(
            plexURLs['moveCollection'].format(
                library=collection.librarySectionID,
                collection_id=collection_id
            ),
            {'after': after_id}
        )

    return None

def updateVisibility(collection, visibility_settings: Visibility):

    params = {}

    ## Request current settings for collection
    data = plex_get(
        plexURLs['manageLibrary'].format(library=collection.librarySectionID),
        {'metadataItemId': collection.ratingKey}
        )

    ## Visibility options are not set for collection if not true
    if 'MediaContainer' in data.keys() and 'Hub' in data['MediaContainer'].keys():

        collection_data = data['MediaContainer']['Hub'][0]

        current_keys = {x: collection_data[x] for x in collection_data.keys() if x in Visibility.keys()}
        params = current_keys

    ## Replace current settings with custom settings
    params = {**params, **visibility_settings.to_dict()}

    ## Update collection visibility
    plex_post(
        plexURLs['manageLibrary'].format(library=collection.librarySectionID), 
        {'metadataItemId': collection.ratingKey, **params}
        )
    
    ## Reload Collection
    collection.reload()

def plex_get(url, params):

    headers = {'Accept': 'application/json'}
    result = requests.get(
        global_vars.PLEX_URL + url,
        params={**params, 'X-Plex-Token': global_vars.PLEX_TOKEN},
        headers=headers
    )
    return json.loads(result.content)

def plex_put(url, params):

    headers = {'Accept': 'application/json', 'X-Plex-Token': global_vars.PLEX_TOKEN}
    result = requests.put(
        global_vars.PLEX_URL + url,
        params=params,
        headers=headers
    )
    return json.loads(result.content)

def plex_post(url, params):

    headers = {'Accept': 'application/json'}
    result = requests.post(
        global_vars.PLEX_URL + url,
        params={**params, 'X-Plex-Token': global_vars.PLEX_TOKEN},
        headers=headers
    )
    return result
