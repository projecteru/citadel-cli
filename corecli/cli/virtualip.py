# coding: utf-8
import click
from citadelpy import CoreAPIError
from prettytable import PrettyTable
from corecli.cli.utils import handle_core_error


@click.argument('node')
@click.pass_context
@handle_core_error
def set_vip(ctx, node):
    core = ctx.obj['coreapi']
    click.echo(core.set_vip(node))


@click.argument('node')
@click.argument('vip')
@click.pass_context
@handle_core_error
def del_vip(ctx, node, vip):
    core = ctx.obj['coreapi']
    click.echo(core.del_vip(node, vip))


@click.argument('from_node')
@click.argument('to_node')
@click.argument('vip')
@click.pass_context
@handle_core_error
def migrate_vip(ctx, from_node, to_node, vip):
    core = ctx.obj['coreapi']
    click.echo(core.migrate_vip(from_node, to_node, vip))


@click.pass_context
@handle_core_error
def list_vip(ctx):
    core = ctx.obj['coreapi']
    resp = core.list_vip()
    table = PrettyTable(['server', 'vip'])
    for vip, server in resp.iteritems():
        table.add_row([server, vip])

    click.echo(table)
