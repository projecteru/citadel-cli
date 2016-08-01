# coding: utf-8
from os.path import expanduser

import click

from corecli.api.client import CoreAPI
from corecli.cli.commands import commands
from corecli.cli.utils import read_json_file, write_json_file


@click.group()
@click.option('--config-path', default=expanduser('~/.corecli.json'), help='config file, json', envvar='CITADEL_CONFIG_PATH')
@click.option('--remotename', default='origin', help='git remote name, default to origin', envvar='CORECLI_REPO_NAME')
@click.pass_context
def core_commands(ctx, config_path, remotename):
    config = read_json_file(config_path)
    if not config:
        config = {}
        config['auth_token'] = click.prompt('Please enter neptulon token')
        config['citadel_url'] = click.prompt('Please enter citadel server url', default='http://127.0.0.1:5003')
        config['mimiron_url'] = click.prompt('Please enter mimiron url', default='')
        write_json_file(config, config_path)

    ctx.obj['coreapi'] = CoreAPI(config['citadel_url'].strip('/'), auth_token=config['auth_token'])
    ctx.obj['remotename'] = remotename
    ctx.obj['mimironurl'] = config['mimiron_url']


for command, function in commands.iteritems():
    core_commands.command(command)(function)


def main():
    core_commands(obj={})
