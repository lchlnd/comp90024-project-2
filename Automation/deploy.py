"""
Main script for dynamic deployment.
Usage: python3 <deploy.py> <config> <system_type> <number_of_instances>
Where: <config>              -- configuration file
       <system_type>         -- streamer / searcher / tweetdb / webserver / site
       <number_of_instances> -- number of instances to create. This must be 4 for system type 'site'.
"""
import re
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
INVENTORY_FILE_PATH = "inventory"

def create_inventory_file(ec2_conn, reservation, type, ip_list, ansible_ssh_user, ansible_ssh_key):
    """Creates inventory file for ansible to run.
        Args:
            ec2_conn:
            reservation:
            type:
            ip_list:
            ansible_ssh_user:
            ansible_ssh_key:
    """
    inventory_file = open(INVENTORY_FILE_PATH, 'w+')
    if type == 'site':
        inventory_file.write('[tweetdb]\n')
        inventory_file.write('tweetdb ansible_ssh_host=' + ip_list[0] + '\n')
        print('Creating volume')
        volume = ec2_conn.create_volume(50, "melbourne-qh2")
        for instance in reservation.instances:
            if instance.private_ip_address == ip_list[0]:
                print ('Attaching volume id ' + volume.id + ' to instance id ' + instance.id)
                ec2_conn.attach_volume(volume.id, instance.id, "/dev/vdc")
        inventory_file.write('[streamer]\n')
        inventory_file.write('streamer ansible_ssh_host=' + ip_list[1] + '\n')
        inventory_file.write('[searcher]\n')
        inventory_file.write('searcher ansible_ssh_host=' + ip_list[2] + '\n')
        inventory_file.write('[webserver]\n')
        inventory_file.write('webserver ansible_ssh_host=' + ip_list[3] + '\n')
    else:
        inventory_file.write('[' + type + ']\n')
        i = 0
        for ip in ip_list:
            inventory_file.write(type + str(i) +' ansible_ssh_host=' + ip + '\n')
            i += 1

        if type == "tweetdb":
            print ('Creating volume')
            for instance in reservation.instances:
                print ('Creating volume')
                volume = ec2_conn.create_volume(25, "melbourne-qh2")
                print ('Attaching volume id ' + volume.id + ' to instance id ' + instance.id)
                ec2_conn.attach_volume(volume.id, instance.id, "/dev/vdc")

    inventory_file.write('[all:vars]\n')
    inventory_file.write('ansible_ssh_user=' + ansible_ssh_user + '\n')
    inventory_file.write('ansible_ssh_private_key_file=' + ansible_ssh_key + '.key\n')
    inventory_file.close()

def orchestrate(type):
    """Orchestrate required system software by executing ansible playbooks.
        Args:
            type:
    """
    if type == 'streamer':
        print ('ansible-playbook streamer.yml -i inventory')
        #os.system('ansible-playbook streamer.yml -i inventory')
    elif type == 'searcher':
        print ('ansible-playbook searcher.yml -i inventory')
        #os.system('ansible-playbook searcher.yml -i inventory')
    elif type == 'tweetdb':
        print ('ansible-playbook tweetdb.yml -i inventory')
        #os.system('ansible-playbook tweetdb.yml -i inventory')
    elif type == 'webserver':
        print ('ansible-playbook webserver.yml -i inventory')
        #os.system('ansible-playbook webserver.yml -i inventory')
    elif type == 'site':
        print ('ansible-playbook site.yml -i inventory')
        #os.system('ansible-playbook site.yml -i inventory')

def create_ip_list(reservation):
    """Create a list containing IP addresses of created instances.
        Args:
            reservation:
    """
    ip_list = list()
    for instance in reservation.instances:
        while (instance.update() != "running"):
            time.sleep(5)
        ip_list.append(instance.private_ip_address)
    return ip_list

def check_cli_argument():
    """Check command line arguments and return configuration parameters in a json object and a list containing all system types.
        Args:
            reservation:

        Returns:
            jconfig:
            sys_type_list:
    """
    if len(sys.argv) != NUM_ARGS:
        logging.error(
            'invalid number of arguments: <deploy.py> <config.json> <system_type> <number_of_instances>'
        )
        sys.exit(ERROR)
    config = sys.argv[1]
    sys_type = sys.argv[2]
    num_instances = int(sys.argv[3])

    with open(config) as fp:
        jconfig = json.load(fp)

    sys_type_list = list()
    for jsys_type in jconfig['system_types']:
        sys_type_list.append(jsys_type['name'])

    if sys_type not in sys_type_list:
        if sys_type != "site":
            logging.error(
                'invalid <system_type>. Please choose one of the system types listed in config.json file.'
            )
            sys.exit(ERROR)
        elif num_instances != 4:
            logging.error(
                'when <system_type> is \'site\'. <number_of_instances> must be 4.'
            )
            sys.exit(ERROR)

    return jconfig, sys_type_list


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    jconfig, sys_type_list = check_cli_argument()
    sys_type = sys.argv[2]
    num_instances = int(sys.argv[3])

    region = RegionInfo(name=jconfig['region']['name'], endpoint=jconfig['region']['endpoint'])

    """Connect to Nectar"""
    print('Connecting to Nectar')
    ec2_conn = boto.connect_ec2(aws_access_key_id=jconfig['credentials']['access_key'],
                                aws_secret_access_key=jconfig['credentials']['secret_key'],
                                is_secure=True, region=region, port=PORT, path=PATH, validate_certs=False)
    ip_list = list()
    """Create instance/s"""
    print('Creating instance')
    if (sys_type == 'site'):
        for type in sys_type_list:
            reservation = ec2_conn.run_instances(max_count=1,
                                                 image_id=jconfig['system_types'][sys_type_list.index(type)][
                                                     'image_id'],
                                                 placement=jconfig['system_types'][sys_type_list.index(type)][
                                                     'placement'],
                                                 key_name=jconfig['key']['name'],
                                                 instance_type=jconfig['system_types'][sys_type_list.index(type)][
                                                     'instance_type'],
                                                 security_groups=jconfig['system_types'][sys_type_list.index(type)][
                                                     'security_groups'])
            while (reservation.instances[0].update() != "running"):
                time.sleep(5)
            ip_list.append(reservation.instances[0].private_ip_address)
            break # t/p
        ip_list.extend(['0.0.0.0','1.1.1.1','2.2.2.2']) # t/p
    else:
        reservation = ec2_conn.run_instances(max_count=num_instances,
                                             image_id=jconfig['system_types'][sys_type_list.index(sys_type)]['image_id'],
                                             placement=jconfig['system_types'][sys_type_list.index(sys_type)]['placement'],
                                             key_name=jconfig['key']['name'],
                                             instance_type=jconfig['system_types'][sys_type_list.index(sys_type)]['instance_type'],
                                             security_groups=jconfig['system_types'][sys_type_list.index(sys_type)]['security_groups'])

        """Get a list of running instances we've created"""
        ip_list = create_ip_list(reservation)
    print('IP addresses of created instances: ' + ', '.join(ip_list))
    """Create inventory file"""
    print ('Creating inventory file')
    create_inventory_file(ec2_conn, reservation, sys_type, ip_list, 'ubuntu', jconfig['key']['name'])

    """Orchestrate instance/s"""
    print ('Orchestrating instance')
    orchestrate(sys_type)
    print ('Completed')