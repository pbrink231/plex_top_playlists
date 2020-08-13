import global_vars
import requests
from utils.logger import log_output

def print_profiles():
    if not global_vars.SONARR_URL or not global_vars.SONARR_TOKEN:
        print('WARNING: Sonarr info not set')
        return

    data = send_request('GET', '/profile')
    if not data:
        print('No data from profiles')
        return

    for profile in data:
        print(f"{profile['id']}: {profile['name']}")

def print_paths():
    if not global_vars.SONARR_URL or not global_vars.SONARR_TOKEN:
        print('WARNING: Sonarr info not set')
        return
    
    data = send_request('GET', '/rootfolder')
    if not data:
        print('No data from root folder')
        return

    for path_data in data:
        print(f"{path_data['path']}")    

def add_series(tvdb_id):
    if not global_vars.SONARR_TOKEN or not global_vars.SONARR_URL or not global_vars.SONARR_PATH or not global_vars.SONARR_PROFILE_ID:
        print('WARNING: Sonarr info not set')
        return

    log_output(f'Adding series {tvdb_id}', 2)

    search_data = search_series(tvdb_id)
    if not search_data:
        print('Series Not Found')
        return

    series_folder = get_series_folder(search_data["title"])

    search_data["profileId"] = global_vars.SONARR_PROFILE_ID
    search_data["qualityProfileId"] = global_vars.SONARR_PROFILE_ID
    search_data["path"] = global_vars.SONARR_PATH + series_folder
    search_data["seasonFolder"] = True
    search_data["monitored"] = True
    search_data["addOptions"] = {
        'ignoreEpisodesWithFiles': False,
        'ignoreEpisodesWithoutFiles': False,
        'searchForMissingEpisodes': False
    }
    # Loop seasons and add monitored to them
    for i in range(len(search_data.get("seasons"))):
        if search_data["seasons"][i]["seasonNumber"] > 0:
            search_data["seasons"][i]["monitored"] = True
            print('season test', search_data["seasons"][i])

    log_output(f'create series data {search_data}', 3)

    data = send_request('post', '/series', json=search_data)
    log_output(f'Returned Search Data {data}', 3)
    if isinstance(data, list):
        log_output(f'ERROR: {search_data["title"]}: Problem adding series', 2)
        for error in data:
            log_output(f'SERIES ADD ERROR: {error["propertyName"]}: {error["errorMessage"]}', 2)
        return

    if data.get('message'):
        log_output(f'{tvdb_id}: Not Added, {data["message"]}', 2)
        return

    if data["title"] == search_data["title"]:
        log_output(f'Series {data["title"]} has been added', 1)
    else:
        log_output(f'Problem adding {data["title"]} to sonarr', 2)

def search_series(tvdb_id):
    if not global_vars.SONARR_TOKEN or not global_vars.SONARR_URL or not global_vars.SONARR_PATH or not global_vars.SONARR_PROFILE_ID:
        log_output('WARNING: Sonarr info not set', 1)
        return

    params = {
        'term': tvdb_id
    }
    data = send_request('GET', '/series/lookup', params=params)
    if not len(data) == 1:
        log_output(f'No Series search data {tvdb_id}', 2)
        return None

    return data[0]



def send_request(method, url, params=None, json=None):
    if not params:
        params = {}

    params['apikey'] = global_vars.SONARR_TOKEN
    full_url = global_vars.SONARR_URL + '/api' + url
    req = requests.request(method, url=full_url, params=params, json=json)
    return req.json()

def get_series_folder(title):
    # FUTURE NOT NEEDED IN V3
    # In V3 will have 'Folder' property with needed value
    naming_config = send_request('get', '/config/naming')
    folder_format = naming_config["seriesFolderFormat"]

    updated_title = title
    # Remove bad characters for file system
    updated_title = updated_title.replace('?', '')
    updated_title = updated_title.replace('?', '')

    # create a dict with possible values
    # possible values
    # {Series Title}{Series.Title}{Series_Title}{Series TitleThe}{Series CleanTitle}{Series.CleanTitle}{Series_CleanTitle}
    # Taken from https://github.com/Sonarr/Sonarr/blob/3fe659587f5d826484ede5078656dc73a507e885/src/NzbDrone.Core/Organizer/FileNameBuilder.cs#L414
    """
        tokenHandlers["{Series Title}"] = m => series.Title;
        tokenHandlers["{Series CleanTitle}"] = m => CleanTitle(series.Title);
        tokenHandlers["{Series CleanTitleYear}"] = m => CleanTitle(TitleYear(series.Title, series.Year));
        tokenHandlers["{Series TitleThe}"] = m => TitleThe(series.Title);
        tokenHandlers["{Series TitleYear}"] = m => TitleYear(series.Title, series.Year);
        tokenHandlers["{Series TitleTheYear}"] = m => TitleYear(TitleThe(series.Title), series.Year);
        tokenHandlers["{Series TitleFirstCharacter}"] = m => TitleThe(series.Title).Substring(0, 1).FirstCharToUpper();
    """

    format_dict = {
        "Series Title": updated_title,
        "Series.Title": updated_title.replace(" ", "."),
        "Series_Title": updated_title.replace(" ", "_")
    }

    return folder_format.format(**format_dict)
