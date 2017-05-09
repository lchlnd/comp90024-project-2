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

def create_inventory(instances):
    with open("inventory2", "w") as f:
        f.write("[webserver]" + os.linesep)
        while (webserver.update() != "running"):
            time.sleep(5)
        f.write("web_1 ansible_ssh_host=%s" % (webserver.private_ip_address) + os.linesep)
        f.write("[streamer]" + os.linesep)
        while (streamer.update() != "running"):
            time.sleep(5)
        f.write("streamer_1 ansible_ssh_host=%s" % (streamer.private_ip_address) + os.linesep)
        f.write("[searcher]" + os.linesep)
        while (searcher.update() != "running"):
            time.sleep(5)
        f.write("searcher_1 ansible_ssh_host=%s" % (searcher.private_ip_address) + os.linesep)
        f.write("[tweetdb]" + os.linesep)
        while (tweetdb.update() != "running"):
            time.sleep(5)
        f.write("tweetdb_1 ansible_ssh_host=%s" % (tweetdb.private_ip_address) + os.linesep)
        f.write("[all:vars]" + os.linesep)
        f.write("ansible_ssh_user=ubuntu" + os.linesep)
        f.write("ansible_ssh_private_key_file=team25.key" + os.linesep)

def create_instance(num_instances = 1):
    return ec2_conn.run_instances(max_count=num_instances,
                                         image_id=jconfig['system_types'][sys_type_list.index(sys_type)]['image_id'],
                                         placement=jconfig['system_types'][sys_type_list.index(sys_type)]['placement'],
                                         key_name=jconfig['key']['name'],
                                         instance_type=jconfig['system_types'][sys_type_list.index(sys_type)][
                                             'instance_type'],
                                         security_groups=jconfig['system_types'][sys_type_list.index(sys_type)][
                                             'security_groups']).instances[0]


def orchestrate(type):
    os.system("ansible-playbook deployment2.yml -i inventory2")

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
    streamer = create_instance(1)

    searcher = create_instance(1)

    tweetdb = create_instance(1)

    webserver = create_instance(1)

    """Create inventory"""



    """Orchestrate instance/s"""
    orchestrate(sys_type)



