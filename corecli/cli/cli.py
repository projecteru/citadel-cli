# -*- coding: utf-8 -*-
import logging
from os import getenv
from os.path import expanduser

import click

from citadelpy import CoreAPI
from corecli.cli.commands import commands
from corecli.cli.utils import read_json_file


@click.group()
@click.option('--zone', help='citadel zone, if not provided, will use citadel server default zone')
@click.option('--config-path', default=expanduser('~/.corecli.json'), help='config file, json', envvar='CITADEL_CONFIG_PATH')
@click.option('--remotename', default='origin', help='git remote name, default to origin', envvar='CORECLI_REPO_NAME')
@click.option('--debug', default=False, help='enable debug output', is_flag=True)
@click.pass_context
def core_commands(ctx, zone, config_path, remotename, debug):
    config = read_json_file(config_path)
    if not config:
        config = {}
        config['auth_token'] = getenv('CITADEL_AUTH_TOKEN')
        config['citadel_url'] = getenv('CITADEL_URL', 'http://citadel.ricebook.net')
        click.echo('config saved to {}'.format(config_path))

    if debug:
        logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(process)d] [%(levelname)s] [%(filename)s @ %(lineno)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S %z')

    if not config['auth_token']:
        raise Exception('CITADEL_AUTH_TOKEN not found')

    coreapi = CoreAPI(config['citadel_url'].strip('/'), auth_token=config['auth_token'], zone=zone)
    ctx.obj['coreapi'] = coreapi
    ctx.obj['remotename'] = remotename
    ctx.obj['debug'] = debug


for command, function in commands.items():
    core_commands.command(command)(function)


def main():
    core_commands(obj={})
