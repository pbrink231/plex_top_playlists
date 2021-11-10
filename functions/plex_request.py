
import json
from dataclasses import dataclass, asdict
import requests

import global_vars
plexURLs = {
    'manageLibrary': '/hubs/sections/{library}/manage',
}


@dataclass
class CollectionRecommendation:

    # metadataItemId: int
    promotedToRecommended: int
    promotedToOwnHome: int
    promotedToSharedHome: int

    def __init__(self, promotedToRecommended=1, promotedToOwnHome=1, promotedToSharedHome=1):

        # self.metadataItemId = metadataItemId

        if type(promotedToRecommended) == int:
            self.promotedToRecommended = promotedToRecommended
        else:
            self.promotedToRecommended = 1 if promotedToRecommended else 0

        if type(promotedToOwnHome) == int:
            self.promotedToOwnHome = promotedToOwnHome
        else:
            self.promotedToOwnHome = 1 if promotedToOwnHome else 0

        if type(promotedToSharedHome) == int:
            self.promotedToSharedHome = promotedToSharedHome
        else:
            self.promotedToSharedHome = 1 if promotedToSharedHome else 0


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

        recomm_keys = asdict(CollectionRecommendation(0))
        current_keys = data['MediaContainer']['Hub'][0]

        current_keys = {x: current_keys[x]
                        for x in current_keys.keys() if x in recomm_keys}
        collection_params = CollectionRecommendation(**current_keys)
        params = {**asdict(collection_params)}

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
