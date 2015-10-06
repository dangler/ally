__author__ = 'jeremiahd'

import click


class AllyCLI(click.MultiCommand):
    """AllyCLI main class"""

    def list_commands(self, ctx):
        return ['ec2']

    def get_command(self, ctx, cmd_name):
        mod = __import__('ally.' + cmd_name, None, None, ['cli'])
        return mod.cli


cli = AllyCLI(help='aws connect cli')

if __name__ == '__main__':
    cli()
