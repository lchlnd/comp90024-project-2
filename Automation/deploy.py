"""
Main script for dynamic deployment.
Usage: python3 <deploy.py> <config.json> <system type> <number of instances>
Where:
"""
import time
import sys
import logging
import json
import boto
import os
import time
from boto.ec2.regioninfo import RegionInfo

NUM_ARGS = 4
ERROR = 2
PORT = 8773
PATH = "/services/Cloud"

def orchestrate(type):
    if type == 'streamer':
        print (1) #here we add ansible commands
    elif type == 'searcher':
        print (2)
    elif type == 'tweetdb':
        print (3)
    elif type == 'webserver':
        print (4)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) != NUM_ARGS:
        logging.error(
            'invalid number of arguments: <deploy.py> <config.json> <system type> <number of instances>'
        )
        sys.exit(ERROR)

    config = sys.argv[1]
    sys_type = sys.argv[2]
    num_instances = sys.argv[3]

    with open(config) as fp:
        jconfig = json.load(fp)

    sys_type_list = list()
    for jsys_type in jconfig['system_types']:
        sys_type_list.append(jsys_type['name'])

    if (sys_type not in sys_type_list):
        logging.error(
            'invalid system type. Please choose one of the system types listed in config.json file.'
        )
        sys.exit(ERROR)

    region = RegionInfo(name=jconfig['region']['name'], endpoint=jconfig['region']['endpoint'])

    """Connect to Nectar"""
    ec2_conn = boto.connect_ec2(aws_access_key_id=jconfig['credentials']['access_key'],
                                aws_secret_access_key=jconfig['credentials']['secret_key'],
                                is_secure=True, region=region, port=PORT, path=PATH, validate_certs=False)

    """Create instance/s"""
    reservation = ec2_conn.run_instances(max_count=num_instances,
                                         image_id=jconfig['system_types'][sys_type_list.index(sys_type)]['image_id'],
                                         placement=jconfig['system_types'][sys_type_list.index(sys_type)]['placement'],
                                         key_name=jconfig['key']['name'],
                                         instance_type=jconfig['system_types'][sys_type_list.index(sys_type)]['instance_type'],
                                         security_groups=jconfig['system_types'][sys_type_list.index(sys_type)]['security_groups'])
    """Orchestrate instance/s"""
    orchestrate(sys_type)



