
import json
from dataclasses import dataclass, asdict
import requests

import global_vars
plexURLs = {
    'manageLibrary': '/hubs/sections/{library}/manage',
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


def update_visibility(plex, section, title, promotedToRecommended=-1, promotedToOwnHome=-1, promotedToSharedHome=-1):

    plex_library = plex.library.section(section)
    collection = plex_library.collection(title)

    custom_setting = {}

    if promotedToRecommended != -1:
        custom_setting['promotedToRecommended'] = promotedToRecommended

    if promotedToOwnHome != -1:
        custom_setting['promotedToOwnHome'] = promotedToOwnHome

    if promotedToSharedHome != -1:
        custom_setting['promotedToSharedHome'] = promotedToSharedHome

    data = plex_get(
        plexURLs['manageLibrary'].format(library=plex_library.key),
        {'metadataItemId': collection.ratingKey}
    )

    params = {}

    if 'MediaContainer' in data.keys() and 'Hub' in data['MediaContainer'].keys():

        collection_data = data['MediaContainer']['Hub'][0]

        current_keys = {x: collection_data[x] for x in collection_data.keys() if x in Visibility.keys()}
        params = {current_keys}

    params = {**params, **custom_setting}

    print(params)

    plex_post(plexURLs['manageLibrary'].format(library=plex_library.key), {
              'metadataItemId': collection.ratingKey, **params})
    plex_library.reload()
    collection.reload()


def plex_get(url, params):

    headers = {'Accept': 'application/json'}
    result = requests.get(
        global_vars.PLEX_URL + url,
        params={**params, 'X-Plex-Token': global_vars.PLEX_TOKEN},
        headers=headers
    )
    print('GET')
    print(result.url)
    print(result.content)
    print(headers)
    return json.loads(result.content)


def plex_post(url, params):

    headers = {'Accept': 'application/json'}
    result = requests.post(
        global_vars.PLEX_URL + url,
        params={**params, 'X-Plex-Token': global_vars.PLEX_TOKEN},
        headers=headers
    )
    print('POST')
    print(result.url)
    print(result)
    print(headers)
    print(result.content)
