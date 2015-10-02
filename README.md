# ally
---
## Description

ally makes working with AWS EC2 instances easier by providing a list of instances you can perform
varies tasks with. Tasks such as list instances, open ssh connection, copy file to, and execute command.

## Installation

```
pip install git+https://bitbucket.org/slalom-consulting/ally
```

## Usage


### ally ec2 ls

List all EC2 instances

```
Usage: ally ec2 ls [OPTIONS]

  list EC2 instances

  All EC2 instances matching the given pattern will be listed.

Options:
  -s, --search-filter TEXT  Pattern in name to filter with
  --help                    Show this message and exit.

```

### ally ec2 ssh

Connect to EC2 instance

```
Usage: ally ec2 ssh [OPTIONS]

  ssh to EC2 instance

  A ssh connection will be opened to EC2 instance matching the given
  pattern. If more than one EC2 instance is found, all instances will be
  displayed so the user can select which instance to connect to.

  The .pem file specified by the EC2 instance will be used. The key must
  exist in the key path location.

Options:
  -s, --search-filter TEXT  Pattern in name to filter with
  -u, --username TEXT       Login username (default = centos)
  -p, --port INTEGER        SSH port (default = 22)
  -k, --key-path PATH       Path to SSH keys (default = ~./ssh)
  --help                    Show this message and exit.
```

### ally ec2 scp FILE

Copy file to EC2 instance
```
Usage: ally ec2 scp [OPTIONS] FILE

  scp file to EC2 instance

  The specified file will be copies to the EC2 instance matching the given
  pattern. If more than one EC2 instance is found, all instances will be
  displayed so the user can select which instance to copy file to.

  The .pem file specified by the EC2 instance will be used. The key must
  exist in the key path location.

Options:
  -s, --search-filter TEXT  Pattern in name to filter with
  -u, --username TEXT       Login username (default = centos)
  -p, --port INTEGER        SSH port (default = 22)
  -k, --key-path PATH       Path to SSH keys (default = ~./ssh)
  -d, --directory PATH      Location on remote server the file is placed
  --help                    Show this message and exit.
```

### ally ec2 exe COMMAND

Execute command on EC2 instance
```
Usage: ally ec2 exe [OPTIONS] COMMAND

  execute command on EC2 instance(s)

  The specified command will be executed on the EC2 instance matching the
  given pattern. If more than one EC2 instance is found, all instances will
  be displayed so the user can select which instance to execute command on.

  The .pem file specified by the EC2 instance will be used. The key must
  exist in the key path location.

Options:
  -s, --search-filter TEXT  Pattern in name to filter with
  -u, --username TEXT       Login username (default = centos)
  -p, --port INTEGER        SSH port (default = 22)
  -k, --key-path PATH       Path to SSH keys (default = ~./ssh)
  --help                    Show this message and exit.
```

## Configuration

AWS credential file should be created at ```~/.aws/credentials```

```
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```


You can also set other defaults at ```~/.aws/config```

```
[default]
region = us-east-1
```

More detailed configurations can be found in the boto3 documentation.

[Boto3 Doc - Configuration](http://boto3.readthedocs.org/en/latest/guide/configuration.html#guide-configuration)