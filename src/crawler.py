import json, requests, time
from datetime import datetime, timedelta
from xml.etree import ElementTree
from xml.dom.minidom import parseString

five_days_ago = datetime.now() - timedelta(days=5)

def crawlGames():
    url = "http://bgg-api-139416041.us-east-1.elb.amazonaws.com/games"
    r = requests.get(url)
    games = json.loads(r.content)

    for game in games:
        if not game["lastUpdatedOn"] or game["lastUIpdatedOn"] < five_days_ago:
            yield game

def crawl():
    has_result = True
    while has_result:
        has_result = False
        for game in crawlGames():
            crawlGame(game["objectId"])
            has_result = True

def crawlUser(username):
    url = "http://bgg-api-139416041.us-east-1.elb.amazonaws.com/collection/%s" % (username)
    
    retry = True

    while retry:
        r = requests.get(url)
        print(r.status_code, r.reason)
        result = json.loads(r.content)

        retry = result['updating']
        print(result)

        if retry:
            time.sleep(3)
        else:
            time.sleep(1)

def iterateOverUsers(xml):
    comments = xml.getElementsByTagName('comment')
    for comment in comments:
        yield comment.getAttribute("username")

def crawlGame(objectId):
    url = "https://www.boardgamegeek.com/xmlapi2/thing?id=%s&ratingcomments=1" % (str(objectId))
    r = requests.post(url)

    xml = parseString(r.content)

    for user in iterateOverUsers(xml):
        crawlUser(user)

    processedGame(objectId)

def processedGame(objectId):
    url = "http://bgg-api-139416041.us-east-1.elb.amazonaws.com/game/%s/processed" % (str(objectId))
    requests.post(url)
    print("Processed Game Id: %s" % (str(objectId)))