import json
import sys

if len(sys.argv) != 2:
    print("Incorrect usage: python3 merger.py <file_to_merge.json>")
    sys.exit(0)

with open('data/sa2.json') as sa2:
    data = json.load(sa2)
    code_dict = {}
    for feature in data['features']:
        code_dict[feature['properties']['SA2_Code_2011']] = feature

fn = sys.argv[1]
with open(fn) as other:
    other_data = json.load(other)

for feature in other_data['features']:
    code = feature['properties']['area_code']
    props = feature['properties']
    del props['area_code']

    if (code in code_dict):
        for k in props:
            code_dict[code]['properties'][k] = props[k]
        DA_CODE = code

with open('data/sa2_dump.json', 'w') as fp:
    json.dump(data, fp)
