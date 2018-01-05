#!/usr/bin/python

USERS = []
NOT_USERS = [
    "frank"
]

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
