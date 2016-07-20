# coding: utf-8

import click
import paramiko
import socket
import os

from corecli.cli.utils import (
    interactive_shell,
    handle_core_error,
    error,
)

def container_login():
    pass

def list_containers():
    pass

@click.argument('cid', required=True)
@click.argument('username', required=True)
@click.option('--port', default=2200)
@click.pass_context
@handle_core_error
def enter_container(ctx, cid, username, port):
    hostname = ctx.obj['mimironurl']
    if not hostname:
        click.echo(error('either set --mimiron-url, or set MIMIRON_URL in environment'))
        ctx.exit(-1)

    pw = os.getenv('MIMIRON_PWD')
    if not pw:
        click.echo(error('password is None. Check MIMIRON_PWD in environment:('))
        ctx.exit(-1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, port))

    t = paramiko.Transport(sock)
    t.start_client()

    username = '{0}~{1}'.format(username, cid)
    t.auth_password(username, pw)
    if not t.is_authenticated():
        click.echo(error('authentication failed. Check MIMIRON_PWD in environment:('))
        t.close()
        ctx.exit(-1)

    chan = t.open_session()
    chan.get_pty()
    chan.invoke_shell()
    interactive_shell(chan)
    chan.close()
    t.close()
