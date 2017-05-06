import couchdb
import json
import sys

DB_NAME = "locations"
DB_LOCATION = "http://127.0.0.1:5984"

try:
    couch = couchdb.Server(DB_LOCATION)
    if DB_NAME in couch:
        db = couch[DB_NAME]
    else:
        db = couch.create(DB_NAME)
except Exception as e:
    sys.exit(2)

with open("data/sa2_coords.json") as fp:
    data = json.load(fp)
    for feature in data['features']:
        feature["_id"] = str(feature["_id"])
        try:
            db.save(feature)

        except couchdb.http.ResourceConflict:
            print("Ignoring duplicate poly.")
