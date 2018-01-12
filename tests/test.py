#!/usr/bin/python

import json
import os
import ConfigParser

config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test.ini')
config = ConfigParser.SafeConfigParser()
config.read(config_file_path)

USERS = json.loads(config.get('Plex', 'users'))
NOT_USERS = json.loads(config.get('Plex', 'not_users'))

def not_user(user):
    if (not USERS or user in USERS) and user not in NOT_USERS:
        print "adding user: {0}".format(
            user
        )
    else:
        print "not adding user: {0}".format(
            user
        )

def empty_user():
    if (not USERS):
        print "empty user array"

if __name__ == "__main__":
    not_user("greg")
    not_user("frank")
    empty_user()
