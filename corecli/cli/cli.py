# coding: utf-8
from os import getenv
from os.path import expanduser

import click
from citadelpy import CoreAPI

from corecli.cli.commands import commands
from corecli.cli.utils import read_json_file, write_json_file, get_username


@click.group()
@click.option('--zone', help='citadel zone, default to c2')
@click.option('--config-path', default=expanduser('~/.corecli.json'), help='config file, json', envvar='CITADEL_CONFIG_PATH')
@click.option('--remotename', default='origin', help='git remote name, default to origin', envvar='CORECLI_REPO_NAME')
@click.option('--debug', default=False, help='enable debug output', envvar='CORECLI_DEBUG', is_flag=True)
@click.pass_context
def core_commands(ctx, zone, config_path, remotename, debug):
    config = read_json_file(config_path)
    if not config:
        config = {}
        config['auth_token'] = getenv('CITADEL_AUTH_TOKEN') or click.prompt('Please enter neptulon token')
        config['citadel_url'] = getenv('CITADEL_URL') or click.prompt('Please enter citadel server url', default='http://127.0.0.1:5003')
        config['mimiron_url'] = getenv('MIMIRON_URL') or click.prompt('Please enter mimiron url', default='')
        config['sso_url'] = getenv('SSO_URL') or click.prompt('Please enter sso url', default='http://sso.ricebook.net')
        config['username'] = get_username(config['sso_url'], config['auth_token'])
        write_json_file(config, config_path)
        click.echo('config saved to {}'.format(config_path))

    coreapi = CoreAPI(config['citadel_url'].strip('/'), username=config['username'], auth_token=config['auth_token'])
    if zone:
        coreapi.zone = zone

    ctx.obj['coreapi'] = coreapi
    ctx.obj['remotename'] = remotename
    ctx.obj['mimironurl'] = config['mimiron_url']
    ctx.obj['debug'] = debug


for command, function in commands.iteritems():
    core_commands.command(command)(function)


def main():
    core_commands(obj={})
