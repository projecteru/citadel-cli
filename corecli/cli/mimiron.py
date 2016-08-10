# coding: utf-8

import click
import paramiko
import socket
import os
from prettytable import PrettyTable

from corecli.cli.utils import (
    interactive_shell,
    handle_core_error,
    error,
)

@click.option('--app', '-a')
@click.option('--entrypoint', '-e')
@click.pass_context
@handle_core_error
def list_containers(ctx,  app, entrypoint):
    core = ctx.obj['coreapi']
    username, _ = core.get_mimiron_container_info()
    info = core.get_mimiron_container_info(username)
    if app:
        info = [t for t in info if t['appname']==app]
    if entrypoint:
        info = [t for t in info if t['entrypoint']==entrypoint]
    table = PrettyTable(['appname', 'entrypoint', 'container_id'])
    [table.add_row([t['appname'], t['entrypoint'], t['cid']]) for t in info]
    click.echo(table)

@click.argument('cid', required=True)
@click.option('--port', default=2200)
@click.pass_context
@handle_core_error
def enter_container(ctx, cid, port):
    core = ctx.obj['coreapi']
    hostname = ctx.obj['mimironurl']
    if not hostname:
        click.echo(error('either set --mimiron-url, or set MIMIRON_URL in environment'))
        ctx.exit(-1)

    username, token = core.get_mimiron_auth_info()
    if not username or not token:
        click.echo(error('username or token is None. Check them in ~/.config.json :('))
        ctx.exit(-1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, port))

    t = paramiko.Transport(sock)
    t.start_client()

    username = '{0}~{1}'.format(username, cid)
    t.auth_password(username, token)
    if not t.is_authenticated():
        click.echo(error('authentication failed. Check username and token in ~/.config.json :('))
        t.close()
        ctx.exit(-1)

    chan = t.open_session()
    chan.get_pty()
    chan.invoke_shell()
    interactive_shell(chan)
    chan.close()
    t.close()
