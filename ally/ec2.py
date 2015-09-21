import re

__author__ = 'jeremiahd'

import subprocess
import sys

import boto3
import botocore
import click


@click.group()
def cli():
    """EC2 group"""
    pass


class SimpleEC2Instance:
    def __init__(self, instance_id, instance_name, private_ip, public_ip, key_name, name_display_width):
        self.instance_id = instance_id
        self.instance_name = instance_name
        self.private_ip = private_ip
        self.public_ip = public_ip
        self.key_name = key_name
        self.name_display_width = name_display_width

    # move to outside function to allow for custom format
    def __str__(self):
        return (str('{} ({})'.format(self.instance_id, self.instance_name)).ljust(self.name_display_width + 15) +
                str(self.private_ip).ljust(20) +
                str(self.public_ip).ljust(20) +
                str(self.key_name).ljust(20))


def transform_list(instances):
    """returns formatted list of instances"""
    formatted_list = []

    name_length = get_max_length(instances)

    for i in instances:
        formatted_list.append(
            SimpleEC2Instance(i.instance_id,
                              get_name(i.tags),
                              i.private_ip_address,
                              i.public_ip_address,
                              i.key_name,
                              name_length))

    return formatted_list


def get_name(instance):
    """get name from instance"""
    if instance is None:
        return ''
    result = [tag['Value'] for tag in instance if tag['Key'] == 'Name']

    return result[0]


def get_max_length(instances):
    for i in instances:
        return max([len(get_name(i.tags)) for i in instances])
    return 0


@cli.command()
@click.option('--search', '-s', 'pattern',
              default='', help='Pattern in name to filter with')
def ls(pattern):
    """list EC2 instances

    All EC2 instances matching the given
    pattern will be listed.
    """
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )

    ec2_list = [i for i in transform_list(instances) if re.search(pattern, i.instance_name)]
    num = 0
    for i in ec2_list:
        click.echo('[{}] {}'.format(num, i))
        num += 1


@cli.command()
@click.option('--search', '-s', 'pattern',
              default='', help='Pattern in name to filter with')
@click.option('--username', '-u', 'username',
              default='centos', help='Login username (default = centos)')
@click.option('--key-path', '-k', 'ssh_path',
              default='~/.ssh', help='Path to SSH keys (default = ~./ssh)', type=click.Path())
@click.option('--port', '-p', 'port', help='SSH port (default = 22)',
              default=22)
def ssh(pattern, username, port, ssh_path):
    """ssh to EC2 instance

    A ssh connection will be opened to EC2
    instance matching the given pattern. If
    more than one EC2 instance is found, all
    instances will be displayed so the user
    can select which instance to connect to.

    The .pem file specified by the EC2
    instance will be used. The key must exist
    in the key path location.

    """

    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )
    ec2_list = transform_list(instances)

    # filter list
    r = re.compile(pattern)
    if pattern is not None:
        ec2_list = [i for i in ec2_list if re.search(pattern, i.instance_name)]

    ec2_instance_num = 0
    if len(ec2_list) == 0:
        click.echo('No ec2 instance matches pattern')
        sys.exit(1)
    elif len(ec2_list) > 1:
        num = 0
        for i in ec2_list:
            click.echo("[{}] {}".format(num, i))
            num += 1

        ec2_instance_num = click.prompt('enter ec2 # to connect to', type=int)
        if ec2_instance_num >= len(ec2_list):
            click.echo('Invalid #', err=True)

    click.echo('... connecting to {}'.format(ec2_list[ec2_instance_num].instance_name))
    instance = ec2_list[ec2_instance_num]

    cmd = 'ssh {}@{} -i {} -p {}'.format(username,
                                         instance.private_ip,
                                         '{}/{}.pem'.format(ssh_path, instance.key_name),
                                         port)
    subprocess.call(cmd, shell=True)
