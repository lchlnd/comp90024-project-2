### Prerequisites Software ###
Ansible

Running this file with python 3 and boto package installed.
Default code:
1. create new instance (number of instance from input)
2. create new inventory file(for ansible)
3. create new volumn
4. attach to first instance created above
5. take a snapshot of above volumn
6. Run ansible command "ansible-playbook database.yml -i inventory -sudo"