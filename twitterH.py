
import sys, getopt
import os
import json
import tweepy
import couchdb
import re
import mpi4py
from mpi4py import MPI

# import nltk.tokenize
# from nltk.tokenize import word_tokenize

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener


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
        if file[i][0] == "0":
            file = file[i]
        i += i

    return file


class MyStreamListener(StreamListener):
    def on_data(self, data):
        tweet = json.loads(data)
        id = tweet["id"]
        text = tweet["text"]
        location = tweet["coordinates"]

        if tweet["coordinates"]:
            doc = {
                'id': id,
                'text': text,
                'location': location
            }

            db.save(doc)
            print("%s :: %s :: %s " % (doc.get('id'), doc.get('text'), doc.get('location')))

    def on_error(self, data):
        print(data)


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

        db = couch.create('db_test')

    except ConnectionError:
        print("connection to couchdb can not be established")
        sys.exit(2)
    except Exception:
        print("data base already exist")
        db = couch['db_test']  # existing
        #sys.exit(2)



    t = MyStreamListener()
    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    twitterStream = Stream(auth, t, wait_on_rate_limit=True)

    # the coordinates of Melbourne
    twitterStream.filter(
        locations=[float(coordinates[1]), float(coordinates[2]), float(coordinates[3]), float(coordinates[4])])



