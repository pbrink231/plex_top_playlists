# plex_top_playlists
A python script to get top weekly or top popular lists and put them in plex as playlists.  It will make a playlist for each user on your server.
This is my first time ever creating a python script.  Also the first time really adding something useful to GitHub

Use at your own risk.  I have it running nightly

## Read This

This script is assuming you are using "Plex Movie" as your library check.  If you are using TMDB, I can add the code here but I personally didnt need it.

The TV Shows playlists give the last episode in your library for the show.  You can easily click the show name to go to it.

The playlists can be created for any of the following
* All shared users
* Specific users by username
* Only the script running user

### What lists this script currently retreives

* Trakt Movie Watched (weekly)
* Trakt Movie Popular
* Trakt Show Watched (weekly)
* Trakt Show Popular
* IMDB top 250 list (http://www.imdb.com/chart/top)

# Getting Started

## Get initial information

### Get plex token

This page will show you where your token is

https://support.plex.tv/hc/en-us/articles/204059436-Finding-an-authentication-token-X-Plex-Token

This page will show you how to view your xml to see that link you grab your token from

https://support.plex.tv/hc/en-us/articles/201998867

### Get Trakt API key

To connect to Trakt you need to get an api key.  You can easily create one.  Here are the steps for that
1) go to Trakt.tv
2) create a user if you dont have one
3) Sign in
4) go here https://trakt.tv/oauth/applications/new
* Name - call it what you want
* Description - needed, put whatever you want
* redirect url - put any websit
* dont need anything else filled out
5) grab the Client ID to use as your Trakt API Key

# Setup - Linux

These instructions are for Ubuntu.  Should also work with Debian or any debian based os.
If you run the script python will yell at you what modules are missing and you can google what you need for your installation.

Install pip:

```bash
sudo apt-get install python-setuptools python-dev build-essential
```

Upgrade pip 

```bash
sudo pip install --upgrade pip
```

Install needed pip modules:

```bash
sudo pip install plexapi
```
There are 2 more modules i dont have the install code for.  If you encounter an error saying something like module missing, please let me know and I will add the correct instructions here.

Create the script file.  Go to the folder location you want to put it

REPLACE user with your user
```bash
sudo mkdir /usr/scripts
sudo chown user:user /usr/scripts
cd /usr/scripts
```

```bash
cp settings.ini.example settings.ini
nano settings.ini
```

Copy conetents from the plex_playlist_update.py file into your new file

Required - Fill in Plex Token
Not Needed - Trakt API key, keep blank for lists
Options - Change folder names and who to sync with

Save and close (hit Ctrl+x, y, enter)

Make the Script executable.  

```bash
sudo chmod +x plex_playlist_update.py
```

Run the script

```bash
./plex_playlist_update.py
```

#### Make script run nightly

```bash
crontab -e
```

Add this line to the bottom of the file (will run at 4:05 am every day)

```bash
5 4 * * * /usr/scripts/plex_playlist_update.py
```

# Setup - Windows

install python 3.  make sure python 3 and pip are both working

```
python --version
```

```
pip --version
```

Add required librarys

```
pip install requests xmltodict parse configparser lxml plexapi urllib2
```

# Used references to create the script

Thank you JonnyWong16 for his amazing scripts which I heavily referenced.

https://gist.github.com/JonnyWong16/2607abf0e3431b6f133861bbe1bb694e
https://gist.github.com/JonnyWong16/b1aa2c0f604ed92b9b3afaa6db18e5fd


