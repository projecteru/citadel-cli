# coding: utf-8

import os
import click

from corecli.api.client import CoreAPI
from corecli.cli.utils import error
from corecli.cli.commands import commands


@click.group()
@click.option('--citadel-url', default=None)
@click.pass_context
def core_commands(ctx, citadel_url):
    citadel_url = citadel_url or os.getenv('CITADEL_URL')
    if not citadel_url:
        click.echo(error('either set --citadel-url, or set CITADEL_URL in environment.'))
        ctx.exit(-1)

    ctx.obj['coreapi'] = CoreAPI(citadel_url)


for command, function in commands.iteritems():
    core_commands.command(command)(function)


def main():
    core_commands(obj={})
