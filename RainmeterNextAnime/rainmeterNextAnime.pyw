# Script for getting next airing anime for Rainmeter skin. Only shows anime you've marked as watching on Anilist.
# ASSIGN USERID & USERNAME in anilistUserInfo.py
# Limit of 90 requests/minute.
# Query gets more information then Rainmeter skin currently uses. Might or might not develop the skin further.

import anilistUserInfo
import requests
import json


# Query func.
def api_request(url, query, variables):
    return requests.post(url, json={'query': query, 'variables': variables}).json()


# Anilist GrapQL url.
url = "https://graphql.anilist.co"

# Query
query = '''
query($userId: Int, $userStatus: MediaListStatus) {
    Page {
        pageInfo {
            total
            hasNextPage
        }
        mediaList(userId: $userId, status: $userStatus, type: ANIME) {
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
    'userId': anilistUserInfo.USERID
}

# make request, save to result.
result = api_request(url, query, variables)

# Create link to anilist profile.
anilistProfileUrl = "https://anilist.co/user/" + anilistUserInfo.USERNAME

# Next airing anime information.
nextTitle = ""
nextEpisode = None
nextTimeUntilAir = None

# iterate animes.
for i in result['data']['Page']['mediaList']:
    if nextTimeUntilAir is None:
        nextTitle = i['media']['title']['userPreferred']
        nextEpisode = i['media']['nextAiringEpisode']['episode']
        nextTimeUntilAir = i['media']['nextAiringEpisode']['timeUntilAiring']
    elif i['media']['nextAiringEpisode']['timeUntilAiring'] < nextTimeUntilAir:
        nextTitle = i['media']['title']['userPreferred']
        nextEpisode = i['media']['nextAiringEpisode']['episode']
        nextTimeUntilAir = i['media']['nextAiringEpisode']['timeUntilAiring']

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

nextEpisodeAndAirTime = "Ep " + str(nextEpisode) + " in " + str(nextAirTimeFormatted)

# Shorten title if over 45 characters, else make it same as nextTitle.
nextTitleShort = (nextTitle[:45] + '..') if len(nextTitle) > 45 else nextTitle

# Create dict with info.
nextAnimeInfoDict = {
    "anilistProfile": anilistUserInfo.USERNAME,
    "anilistProfileUrl": anilistProfileUrl,
    "title": nextTitle,
    "titleShort": nextTitleShort,
    "episode": nextEpisode,
    "timeUntilAir": nextAirTimeFormatted,
    "episodeAndAirTime": nextEpisodeAndAirTime
}

# Create file rainmeter skin can read from, write dict as json to file.
with open('nextAiringAnime.txt', 'w') as outfile:
    json.dump(nextAnimeInfoDict, outfile)

# Rainmeter couldnt run file sometimes, Close written file and exit script. (Solved problem...i think)
outfile.close()
exit()
