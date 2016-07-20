# coding: utf-8

import click

from corecli.api.client import CoreAPI
from corecli.cli.utils import error
from corecli.cli.commands import commands


@click.group()
@click.option('--citadel-url', default=None, help='url for CITADEL', envvar='CITADEL_URL')
@click.option('--remotename', default='origin', help='git remote name, default to origin', envvar='CORECLI_REPO_NAME')
@click.pass_context
def core_commands(ctx, citadel_url, remotename):
    if not citadel_url:
        click.echo(error('either set --citadel-url, or set CITADEL_URL in environment.'))
        ctx.exit(-1)

    ctx.obj['coreapi'] = CoreAPI(citadel_url.strip('/'))
    ctx.obj['remotename'] = remotename


for command, function in commands.iteritems():
    core_commands.command(command)(function)


def main():
    core_commands(obj={})
