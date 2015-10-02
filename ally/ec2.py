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


def get_instances(search_filter):
    """returns formatted list of instances"""
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )

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

    ec2_list = [i for i in formatted_list if re.search(search_filter, i.instance_name)]

    return sorted(ec2_list, key=lambda i: i.instance_name)


def get_instance(ec2_list):
    """returns a single instance the user selected or a collection the user selected"""
    if len(ec2_list) == 0:
        click.echo('No ec2 instance matches pattern')
        sys.exit(1)
    else:
        num = 1
        for i in ec2_list:
            click.echo("[{}] {}".format(num, i))
            num += 1

        response = click.prompt('Select instance(s), use commas to select multiple instances (0 to cancel)')

        if str(response).isdigit():
            if int(response) == 0:
                sys.exit()
            if int(response) > len(ec2_list):
                click.echo('Invalid #', err=True)
                sys.exit(1)

            instance = ec2_list[int(response) - 1]
            return instance
        else:
            selections = str(response).split(',')
            instances = []
            for selection in selections:
                if int(selection) > len(ec2_list):
                    click.echo("{} is an invalid selection".format(selection), err=True)
                    sys.exit(1)
                instances.append(ec2_list[int(selection) - 1])

            return instances


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
@click.option('--search-filter', '-s',
              default='', help='Pattern in name to filter with')
def ls(search_filter):
    """list EC2 instances

    All EC2 instances matching the given
    pattern will be listed.
    """
    ec2_list = get_instances(search_filter)

    num = 1
    for i in ec2_list:
        click.echo('[{}] {}'.format(num, i))
        num += 1


@cli.command()
@click.option('--search-filter', '-s',
              default='', help='Pattern in name to filter with')
@click.option('--username', '-u',
              default='centos', help='Login username (default = centos)')
@click.option('--port', '-p', 'port', help='SSH port (default = 22)',
              default=22)
@click.option('--key-path', '-k',
              default='~/.ssh', help='Path to SSH keys (default = ~./ssh)',
              type=click.Path())
def ssh(search_filter, username, port, key_path):
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
    ec2_list = get_instances(search_filter)

    instance = get_instance(ec2_list)

    if isinstance(instance, list):
        click.echo('this command doesn\'t support connecting to multiple instances')
        sys.exit(1)

    cmd = 'ssh -i {} -p {} {}@{}'.format('{}/{}.pem'.format(key_path, instance.key_name),
                                         port,
                                         username,
                                         instance.private_ip)

    click.echo('..connecting to {} @ {}'.format(instance.instance_name, instance.private_ip))
    subprocess.call(cmd, shell=True)


@cli.command()
@click.argument('file')
@click.option('--search-filter', '-s',
              default='', help='Pattern in name to filter with')
@click.option('--username', '-u',
              default='centos', help='Login username (default = centos)')
@click.option('--port', '-p', help='SSH port (default = 22)',
              default=22)
@click.option('--key-path', '-k',
              default='~/.ssh', help='Path to SSH keys (default = ~./ssh)',
              type=click.Path())
@click.option('--directory', '-d',
              default='~', help='Location on remote server the file is placed',
              type=click.Path())
def scp(search_filter, username, port, key_path, file, directory):
    """scp file to EC2 instance

    The specified file will be copies to
    the EC2 instance matching the given
    pattern. If more than one EC2 instance
    is found, all instances will be
    displayed so the user can select which
    instance to copy file to.

    The .pem file specified by the EC2
    instance will be used. The key must exist
    in the key path location.

    """
    ec2_list = get_instances(search_filter)

    instance = get_instance(ec2_list)

    if isinstance(instance, list):
        for i in instance:
            cmd = 'scp -i {} -P {} {} {}@{}:{}'.format('{}/{}.pem'.format(key_path, i.key_name),
                                                       port,
                                                       file,
                                                       username,
                                                       i.private_ip,
                                                       directory)

            click.echo('..coping file {} to {}({})'.format(file, i.instance_name, i.private_ip))
            subprocess.call(cmd, shell=True)
    else:
        cmd = 'scp -i {} -P {} {} {}@{}:{}'.format('{}/{}.pem'.format(key_path, instance.key_name),
                                                   port,
                                                   file,
                                                   username,
                                                   instance.private_ip,
                                                   directory)

        click.echo('..coping file {} to {}({})'.format(file, instance.instance_name, instance.private_ip))
        subprocess.call(cmd, shell=True)


@cli.command()
@click.argument('command')
@click.option('--search-filter', '-s',
              default='', help='Pattern in name to filter with')
@click.option('--username', '-u',
              default='centos', help='Login username (default = centos)')
@click.option('--port', '-p', 'port', help='SSH port (default = 22)',
              default=22)
@click.option('--key-path', '-k',
              default='~/.ssh', help='Path to SSH keys (default = ~./ssh)',
              type=click.Path())
def exe(search_filter, username, port, key_path, command):
    """execute command on EC2 instance(s)

    The specified command will be executed
    on the EC2 instance matching the given
    pattern. If more than one EC2 instance
    is found, all instances will be
    displayed so the user can select which
    instance to execute command on.

    The .pem file specified by the EC2
    instance will be used. The key must exist
    in the key path location.

    """
    ec2_list = get_instances(search_filter)

    instance = get_instance(ec2_list)

    if isinstance(instance, list):
        for i in instance:
            cmd = 'ssh -t -i {} -p {} {}@{} \'{}\''.format('{}/{}.pem'.format(key_path, i.key_name),
                                                        port,
                                                        username,
                                                        i.private_ip,
                                                        command)

            click.echo('..executing {} on {}({})'.format(command, i.instance_name, i.private_ip))
            subprocess.call(cmd, shell=True)

    else:
        cmd = 'ssh -t -i {} -p {} {}@{} \'{}\''.format('{}/{}.pem'.format(key_path, instance.key_name),
                                                    port,
                                                    username,
                                                    instance.private_ip,
                                                    command)

        click.echo('..executing {} on {}({})'.format(command, instance.instance_name, instance.private_ip))
        subprocess.call(cmd, shell=True)
