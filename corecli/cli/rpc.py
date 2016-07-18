# coding: utf-8

import click
from prettytable import PrettyTable

from corecli.cli.utils import error, handle_core_error


@click.pass_context
@handle_core_error
def get_networks(ctx):
    core = ctx.obj['coreapi']
    ns = core.get_networks()

    table = PrettyTable(['name', 'id', 'type', 'CIDR'])
    for n in ns:
        cidrs = [c.get('PreferredPool', '') for c in n.get('ipamV4Config', [])]
        table.add_row([n['name'], n['id'], n['networkType'], ','.join(cidrs)])
    click.echo(table)


@click.argument('podname', required=False)
@click.pass_context
@handle_core_error
def get_pod(ctx, podname):
    core = ctx.obj['coreapi']

    if not podname:
        pods = core.get_pods()

        table = PrettyTable(['name', 'desc'])
        for p in pods:
            table.add_row([p['name'], p['desc']])
        click.echo(table)
        return

    pod = core.get_pod(podname)
    if not pod:
        click.echo(error('Pod %s not found' % podname))
        ctx.exit(-1)

    table = PrettyTable(['name', 'desc'])
    table.add_row([pod['name'], pod['desc']])
    click.echo(table)
