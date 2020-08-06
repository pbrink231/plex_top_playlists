""" Methods to pull user information from Plex """
import requests
import xmltodict
import global_vars

def get_all_users(plex):
    """ Get all Plex Server users respecting settings.ini """
    machine_id = plex.machineIdentifier
    headers = {'Accept': 'application/json', 'X-Plex-Token': global_vars.PLEX_TOKEN}
    result = requests.get(
        'https://plex.tv/api/servers/{server_id}/shared_servers?X-Plex-Token={token}'.format(
            server_id=machine_id,
            token=global_vars.PLEX_TOKEN
        ),
        headers=headers
    )
    xml_data = xmltodict.parse(result.content)

    result2 = requests.get('https://plex.tv/api/users', headers=headers)
    xml_data_2 = xmltodict.parse(result2.content)

    users = {}
    user_ids = {}
    if 'User' in xml_data_2['MediaContainer'].keys():
        # has atleast 1 shared user generally
        user_ids = {plex_user['@id']: plex_user.get('@username', plex_user.get('@title')) for plex_user in xml_data_2['MediaContainer']['User']}


    if 'SharedServer' in xml_data['MediaContainer']:
        # has atlease 1 shared server
        if isinstance(xml_data['MediaContainer']['SharedServer'], list):
            # more than 1 shared user
            for server_user in xml_data['MediaContainer']['SharedServer']:
                users[user_ids[server_user['@userID']]] = server_user['@accessToken']
        else:
            # only 1 shared user
            server_user = xml_data['MediaContainer']['SharedServer']
            users[user_ids[server_user['@userID']]] = server_user['@accessToken']

    return users


def get_user_tokens(plex):
    """ Get the token for a user to connect to plex as them """
    users = get_all_users(plex)
    allowed_users = {}
    for user in users:
        if ((not global_vars.ALLOW_SYNCED_USERS or user in global_vars.ALLOW_SYNCED_USERS) and
                user not in global_vars.NOT_ALLOW_SYNCED_USERS):
            allowed_users[user] = users[user]

    return allowed_users
