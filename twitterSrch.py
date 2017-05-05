import sys
import jsonpickle
import os
import tweepy
import json
import couchdb
import re

def main(argv):
    name = argv[0]
    configFile = argv[1]

    return name, configFile


def reading_files(fName):
    file = []

    path = os.path.abspath(__file__)
    try:
        if os.path.exists(path):
            with open(fName, "r") as f:

                for line in f:
                    line = line.strip("\n")
                    item = re.split('[ \t,]+', line)
                    file.append(item)


    except FileNotFoundError:
        print("Could not find file:", fName)
        sys.exit(2)
    i = 0
    for i in range(len(file)):
        if file[i][0] == "1":
            file = file[i]
        i += i

    return file

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print('invalid number of arguments: <file_name.py> <authentication file> <coordinates file>')
        sys.exit(2)
    else:
        a_file, c_file = main(sys.argv[1:])


    authentication = reading_files(a_file)
    coordinates = reading_files(c_file)
    ckey = authentication[1]
    csecret = authentication[2]
    atoken = authentication[3]
    asecret = authentication[4]

    server = authentication[5]
    couch = couchdb.Server(server)
    try:

        db = couch['db_test']

    except ConnectionError:
        print("connection to couchdb can not be established")
        sys.exit(2)
    except Exception:
        print("database does not exist")
        db = couch.create('db_test')

    # Replace the API_KEY and API_SECRET with your application's key and secret.
    auth = tweepy.AppAuthHandler(ckey, csecret)

    api = tweepy.API(auth, wait_on_rate_limit=True,
                       wait_on_rate_limit_notify=True)

    if not api:
        print ("Can't Authenticate")
        sys.exit(-1)


    maxTweets = 100000 # Some arbitrary large number
    tweetsPerQry = 100  # this is the max the API permits


    # If results from a specific ID onwards are reqd, set since_id to that ID.
    # else default to no lower limit, go as far back as API allows
    sinceId = None

    # If results only below a specific ID are, set max_id to that ID.
    # else default to no upper limit, start from the most recent tweet matching the search query.



    max_id = -1

    tweetCount = 0

    while True :

        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(q="*", geocode="-37.9994,144.5937,50km", count=tweetsPerQry)

                else:
                    new_tweets = api.search(q="*", geocode="-37.9994,144.5937,50km", count=tweetsPerQry,
                                            since_id=sinceId)
            else:
                if (not sinceId):
                    new_tweets = api.search(q="*", geocode="-37.9994,144.5937,50km", count=tweetsPerQry,
                                            max_id=str(max_id - 1))
                else:
                    new_tweets = api.search(q="*", geocode="-37.9994,144.5937,50km", count=tweetsPerQry,
                                            max_id=str(max_id - 1),
                                            since_id=sinceId)
            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:

                id = tweet.id
                text = tweet.text
                location = tweet.coordinates

                json = tweet._json

                if tweet.coordinates or tweet.place:
                    json['_id'] = str(json['id'])
                    try:
                        db.save(json)
                    except couchdb.http.ResourceConflict:
                        print("ignore duplicated tweet")

            tweetCount += len(new_tweets)
            print("Downloaded {0} tweets".format(tweetCount))
            max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            # Just exit if any error
            print("some error : " + str(e))
            break

    print ("Downloaded {0} tweets, Saved to {1}".format(tweetCount),"tweets")