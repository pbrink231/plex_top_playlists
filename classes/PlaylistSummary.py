import requests

class PlaylistSummary(object):
    """__init__() functions as the class constructor"""
    def __init__(self, database_type, name, list_ids):
        self.database_type = database_type
        self.name = name
        self.list_ids = list_ids
        self.matching_ids = []

    def missing_ids(self):
        return list(set(self.list_ids) - set(self.matching_ids))

    
    def found_info(self):
        if (self.database_type == "imdb"):
            print("""
        {match_ids_len} of {imdb_ids_len} found in {database_type} list:
            {playlist_name}
        That means you are MISSING:
            {miss_ids_len}""".format(
            database_type=self.database_type,
            playlist_name=self.name,
            match_ids_len=len(self.matching_ids),
            imdb_ids_len=len(self.list_ids),
            miss_ids_len=len(self.missing_ids())
            ))

    def missing_info(self, columns=4):
        missing_ids = self.missing_ids()
        if len(missing_ids) > 0:
            if (self.database_type == "imdb"):
                print("""
        The IMDB IDs are listed below.
        Radarr can use these in the search.  Just Copy/Paste
        """)
            if (self.database_type == "tvdb"):
                print("""
    The TVDB IDs are listed below.
    Sonarr can use these in the search.  Just Copy/Paste
    """)
            for i in range(len(missing_ids)):
                print("{}:{}".format(self.database_type, missing_ids[i]), end='')
                print('\t', end='')
                if i != 0 and i != len(missing_ids) and (not (i + 1) % columns):
                    print()
            print("\n\n")
        else:
            print("""
    Not missing any
    """)

    def send_to_discord(self, discord_url):
        missing_ids = self.missing_ids()
        message = {}
        id_list = ""
        for i in range(len(missing_ids)):
            id_list+= '`' + self.database_type + missing_ids[i] + '`'
            print('\t', end='')
            if i != len(missing_ids):
                id_list+='  |  '
            if i != 0 and i != len(missing_ids) and (not (i + 1) % 4):
                id_list+='\n'
        
        first_part = {}
        first_part["title"] = self.name
        first_part["description"] = """
        {match_ids_len} of {imdb_ids_len} found in list:
        MISSING: {miss_ids_len}
        
        {show_list}""".format(
            playlist_name=self.name,
            match_ids_len=len(self.matching_ids),
            imdb_ids_len=len(self.list_ids),
            miss_ids_len=len(self.missing_ids()),
            show_list=id_list)

        # first_part["color"] = 1127128
        message['embeds'] = [first_part]
        r = requests.post(discord_url, headers={"Content-Type":"application/json"}, json=message)

