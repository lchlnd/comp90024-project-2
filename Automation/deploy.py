"""
Main script for dynamic deployment.
Usage: python3 <deploy.py> <config.json> <number of instances>
Where:
"""

import sys
import logging
import json
import boto
import os
import time
from boto.ec2.regioninfo import RegionInfo

NUM_ARGS = 3
ERROR = 2
PORT = 8773
PATH = "/services/Cloud"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) != NUM_ARGS:
        logging.error(
            'invalid number of arguments: <deploy.py> <config.json> <number of instances>'
        )
        sys.exit(ERROR)

    config = sys.argv[1]
    num_instances = sys.argv[2]

    with open(config) as fp:
        jconfig = json.load(fp)

    region = RegionInfo(name=jconfig['region']['name'], endpoint=jconfig['region']['endpoint'])

    """Connect to Nectar"""
    ec2_conn = boto.connect_ec2(aws_access_key_id=jconfig['credentials']['access_key'],
                            aws_secret_access_key=jconfig['credentials']['secret_key'],
                            is_secure=True, region=region, port=PORT, path=PATH, validate_certs=False)
    security_group_names = list()

    for security_grp in jconfig['security_groups']:
        security_group_names.append(security_grp['name'])

    """Create instance/s"""
    ec2_conn.run_instances(image_id=jconfig['image_id'], placement=jconfig['placement'], key_name=jconfig['key']['name'],
                       instance_type=jconfig['instance_type'], security_groups=security_group_names)
