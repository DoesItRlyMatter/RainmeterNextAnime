# Script for getting next airing anime for Rainmeter skin. Only shows anime you've marked as watching on Anilist.
# ASSIGN USERID & USERNAME in anilistUserInfo.py
# Limit of 90 requests/minute.
# Query gets more information then Rainmeter skin currently uses. Might or might not develop the skin further.

# import anilistUserInfo
import configparser
import requests
import json
import sys
import os

config = configparser.ConfigParser()


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# Query func.
def api_request(url, query, variables):
    return requests.post(url, json={'query': query, 'variables': variables}).json()


# read config file & assign values to vars for ease of use.
config = configparser.ConfigParser()
config.read(resource_path('config.ini'))

# Makes USERNAME "DoesItReallyMatter" if empty or something wrong with .ini
try:
    if config['ANILISTUSER']['USERNAME'] == "":
        USERNAME = "DoesItReallyMatter"
    else:
        USERNAME = config['ANILISTUSER']['USERNAME']
except (KeyError):
    USERNAME = "DoesItReallyMatter"

# Anilist GrapQL url.
url = "https://graphql.anilist.co"

# Query
query = '''
query($userName: String, $userStatus: MediaListStatus) {
    Page {
        pageInfo {
            total
            hasNextPage
        }
        mediaList(userName: $userName, status: $userStatus, type: ANIME) {
            media {
                title {
                    userPreferred
                }
                episodes
                nextAiringEpisode {
                    episode
                    timeUntilAiring
                }
                format
                coverImage {
                    large
                }
                status
            }
            status
        }
    }
}
'''
# Query variables, what to get.
variables = {
    'userStatus': "CURRENT",
    'userName': USERNAME
}

# make request, save to result.
result = api_request(url, query, variables)

# Create link to anilist profile.
anilistProfileUrl = "https://anilist.co/user/" + USERNAME

# User following
followingReleasingAnimeCount = 0
# Next airing anime information.
nextTitle = str()
nextEpisode = str()
nextTimeUntilAir = 0
nextTitleShort = str()
nextAirTimeFormatted = str()
nextEpisodeAndAirTime = str()

# iterate animes.
for i in result['data']['Page']['mediaList']:
    # Check if anime is releasing episodes.
    try:
        if(i['media']['status'] == "RELEASING"):
            # check if its the first iteration, save the values.
            followingReleasingAnimeCount += 1
            if nextTimeUntilAir == 0:
                nextTitle = i['media']['title']['userPreferred']
                nextEpisode = i['media']['nextAiringEpisode']['episode']
                nextTimeUntilAir = i['media']['nextAiringEpisode']['timeUntilAiring']
            # check if anime has less time until new episode.
            elif i['media']['nextAiringEpisode']['timeUntilAiring'] < nextTimeUntilAir:
                nextTitle = i['media']['title']['userPreferred']
                nextEpisode = i['media']['nextAiringEpisode']['episode']
                nextTimeUntilAir = i['media']['nextAiringEpisode']['timeUntilAiring']
    except (TypeError):
        # TypeError sometimes, cant be arsed to look up why.
        # print("Shit hit the fan...")
        pass

# If watching releasing anime, else skip.
if followingReleasingAnimeCount != 0:
    # format variables
    # convert time until airing to days, hours, minutes and seconds. Use whatevers needed.
    day = nextTimeUntilAir // (24*3600)
    nextTimeUntilAir = nextTimeUntilAir % (24 * 3600)
    hour = nextTimeUntilAir // 3600
    nextTimeUntilAir %= 3600
    minutes = nextTimeUntilAir // 60
    nextTimeUntilAir %= 60
    seconds = nextTimeUntilAir

    # Remove days, hours if 0.
    if day < 1:
        nextAirTimeFormatted = ("%dh %dm" % (hour, minutes))
    elif hour < 1:
        nextAirTimeFormatted = ("%dm" % (minutes))
    else:
        nextAirTimeFormatted = ("%dd %dh %dm" % (day, hour, minutes))

    # Concat Episode number with time until next episode.
    nextEpisodeAndAirTime = "Ep " + str(nextEpisode) + " in " + str(nextAirTimeFormatted)
    # Shorten title if over 45 characters, else make it same as nextTitle.
    nextTitleShort = (nextTitle[:45] + '..') if len(nextTitle) > 45 else nextTitle

# Create dict with info.
nextAnimeInfoDict = {
    "anilistProfile": USERNAME,
    "anilistProfileUrl": anilistProfileUrl,
    "followingReleasingCount": str(followingReleasingAnimeCount),
    "title": nextTitle,
    "titleShort": nextTitleShort,
    "episode": nextEpisode,
    "timeUntilAir": nextAirTimeFormatted,
    "episodeAndAirTime": nextEpisodeAndAirTime
}

# Create file rainmeter skin can read from, write dict as json to file.
with open(resource_path('nextAiringAnime.txt'), 'w') as outfile:
    json.dump(nextAnimeInfoDict, outfile)

# Rainmeter couldnt run file sometimes, Close written file and exit script. (Solved problem...i think)
outfile.close()
exit()
