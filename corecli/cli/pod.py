# coding: utf-8

import click
from prettytable import PrettyTable

from corecli.cli.utils import error, handle_core_error


@click.argument('podname')
@click.pass_context
@handle_core_error
def get_memcap(ctx, podname):
    core = ctx.obj['coreapi']
    res = core.get_memcap(podname)
    table = PrettyTable(['node', 'total', 'used', 'used_by_memcap', 'diff'])
    for node, info in res.iteritems():
        table.add_row([node, info['total'], info['used'], info['used_by_memcap'], info['diff']])

    click.echo(table)


@click.argument('podname')
@click.pass_context
@handle_core_error
def sync_memcap(ctx, podname):
    core = ctx.obj['coreapi']
    res = core.sync_memcap(podname)
    click.echo(res)
