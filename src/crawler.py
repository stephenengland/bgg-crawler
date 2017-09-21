import json, requests, time
from datetime import datetime, timedelta
from xml.etree import ElementTree
from xml.dom.minidom import parseString
from requests.exceptions import Timeout, ReadTimeout

five_days_ago = datetime.now() - timedelta(days=5)

def crawlGames():
    url = "http://bgg-api-139416041.us-east-1.elb.amazonaws.com/games"
    r = requests.get(url)
    games = json.loads(r.content)

    for game in games:
        if not game["lastUpdatedOn"] or game["lastUIpdatedOn"] < five_days_ago:
            yield game

    print("Processed All Games")

def crawl():
    has_result = True
    while has_result:
        has_result = False
        for game in crawlGames():
            crawlGame(game["objectId"])
            has_result = True

    print("Stopping successfully")

def crawlUser(username):
    url = "http://bgg-api-139416041.us-east-1.elb.amazonaws.com/collection/%s" % (username)
    
    retry = True
    retry_count = 0

    while retry and retry_count < 10:
        retry_count += 1
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == requests.codes.ok:
                result = json.loads(r.content)

                retry = result['updating']

                if retry:
                    time.sleep(3)
                else:
                    retry = False
                    time.sleep(1)
            else:
                print(r.status_code, r.reason)
                retry = False
                time.sleep(25)
        except (Timeout, ReadTimeout) as ex:
            print("Timeout getting user collection")
            time.sleep(30)

    print("Crawled %s" % (username))

def iterateOverUsers(xml):
    comments = xml.getElementsByTagName('comment')
    for comment in comments:
        yield comment.getAttribute("username")

def getType(xml):

    items = xml.getElementsByTagName('item')

    for item in items:
        return item.getAttribute("type")

def crawlGame(objectId):
    url = "https://www.boardgamegeek.com/xmlapi2/thing?id=%s&ratingcomments=1" % (str(objectId))
    try:
        r = requests.post(url, timeout=60)

        xml = parseString(r.content)

        boardgame_type = getType(xml)

        for user in iterateOverUsers(xml):
            crawlUser(user)

        processedGame(objectId, boardgame_type)
    except (Timeout, ReadTimeout) as ex:
        print("Timeout getting game")

def processedGame(objectId, boardgame_type):
    if boardgame_type == "boardgameexpansion":
        url = "http://bgg-api-139416041.us-east-1.elb.amazonaws.com/game/%s/processed?expansion=1" % (str(objectId))
    else:
        url = "http://bgg-api-139416041.us-east-1.elb.amazonaws.com/game/%s/processed" % (str(objectId))

    try:
        requests.post(url, timeout=60)
        print("Processed Game Id: %s" % (str(objectId)))
    except (Timeout, ReadTimeout) as ex:
        print("Timeout processing game")
