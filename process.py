"""
Process raw tweets and store in new database.

Only id is kept, with SA2 and sentiment added.
Polygon matching sourced from
https://gis.stackexchange.com/questions/208546/check-if-a-point-falls-within-a-multipolygon-with-python
"""

import couchdb
import logging
import sys
import fiona
import time
from tweetAnalyzer import TweetAnalyzer
from shapely.geometry import shape, Point


DB_LOC = "locations"
DB_RAW = "raw_tweets"
DB_PRO = "processed_tweets"
DB_ADDRESS = "http://127.0.0.1:5984"
GEO_JSON = "web/data/sa2_dump.json"


def tag_tweets(db_raw, db_pro, multipol):
    """Tag raw tweets with SA2 and store in processed db."""
    for id in db_raw:

        # Hack way to not double process.
        if id in db_pro:
            continue

        # Get tweet.
        tweet = db_raw[id]

        # Look for exact coordinates in tweet.
        if tweet['coordinates']:
            coords = tweet['coordinates']
        # Get the midpoint of place.
        elif tweet['place']:
            coords = average_bounding_box(
                tweet['place']['bounding_box']['coordinates']
            )

        # Attempt to process if location exists.
        if coords:
            point = Point(coords)
            code = None
            for multi in multipol:
                if point.within(shape(multi['geometry'])):
                    code = multi['properties']['SA2_Code_2011']

                    sentiment = TweetAnalyzer(tweet).analyzeSentiment()
                    stored_tweet = {
                        '_id': id, 'code': code,
                        'text': tweet['text'], 'sentiment': sentiment
                        }
                    db_pro.save(stored_tweet)


def average_bounding_box(box):
    """Average list of 4 bounding box coordinates to a midpoint."""
    lng = 0
    lat = 0
    for i in range(len(box[0])):
        lng += box[0][i][0]
        lat += box[0][i][1]
    lat /= 4
    lng /= 4

    return lng, lat


if __name__ == "__main__":
    # Read locations into memory.
    multipol = fiona.open(GEO_JSON)

    # Get raw tweets db.
    couch = couchdb.Server(DB_ADDRESS)
    try:
        db_raw = couch[DB_RAW]
    except Exception:
        logging.error("Raw tweets DB does not exist.")
        sys.exit(2)

    # Get processed tweets db.
    if DB_PRO in couch:
        db_pro = couch[DB_PRO]
    else:
        db_pro = couch.create(DB_PRO)

    # Tag and store tweets.
    while True:
        tag_tweets(db_raw, db_pro, multipol)
        time.sleep(1200)

