import sys
import logging
import json
import couchdb
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener


class TwitterStreamListener(StreamListener):
    def on_data(self, data):
        jtweet = json.loads(data)
        jtweet['_id'] = str(jtweet['id'])
        try:
            db.save(jtweet)
        except couchdb.http.ResourceConflict:
            print("ignore duplicated tweet")

    def on_error(self, status_code):
        print(status_code)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        logging.error('invalid number of arguments: <tweetStreamer.py> <config.json>')
        sys.exit(2)

with open(sys.argv[1]) as config_file:
    jconfig = json.load(config_file)

try:
    server = jconfig['Servers'][0]  # first server in config.json
    couch = couchdb.Server(server)

    if jconfig['DatabaseName'] in couch:
        print("database already exists")
        db = couch['raw_tweets']
    else:
        print("create new database")
        db = couch.create('raw_tweets')

except Exception as e:
    logging.error(str(e))
    sys.exit(2)

ckey = jconfig['Authentication'][1]['ConsumerKey']
csecret = jconfig['Authentication'][1]['ConsumerSecret']
atoken = jconfig['Authentication'][1]['AccessToken']
asecret = jconfig['Authentication'][1]['AccessTokenSecret']

streamListener = TwitterStreamListener()
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)
twitterStream = Stream(auth, streamListener, wait_on_rate_limit=True)

# the coordinates of Melbourne
twitterStream.filter(
    locations=[float(jconfig['Coordinates'][0]), float(jconfig['Coordinates'][1]), float(jconfig['Coordinates'][2]),
               float(jconfig['Coordinates'][3])])
