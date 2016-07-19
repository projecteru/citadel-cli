# coding: utf-8

import os
import yaml
import click
import envoy
from functools import wraps
import socket
import sys
import termios
import tty
from paramiko.py3compat import u

from corecli.api.client import CoreAPIError


def warn(text):
    return click.style(text, fg='yellow')


def error(text):
    return click.style(text, fg='red', bold=True)


def normal(text):
    return click.style(text, fg='white')


def info(text):
    return click.style(text, fg='green')


def handle_core_error(f):
    @wraps(f)
    def _(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except CoreAPIError as e:
            click.echo(error(e.message))
            ctx = click.get_current_context()
            ctx.exit(-1)
    return _


def get_commit_hash(cwd=None):
    """拿cwd的最新的commit hash."""
    r = envoy.run('git rev-parse HEAD', cwd=cwd)
    if r.status_code:
        return ''
    return r.std_out.strip()


def get_remote_url(cwd=None, remote='origin'):
    """拿cwd的remote的url.
    发现envoy.run的command只能是bytes, 不能是unicode.
    """
    r = envoy.run('git remote get-url %s' % str(remote), cwd=cwd)
    if r.status_code:
        return ''
    return r.std_out.strip()


def get_appname(cwd=None):
    try:
        with open(os.path.join(cwd or os.getcwd(), 'app.yaml'), 'r') as f:
            specs = yaml.load(f)
    except IOError:
        return ''
    return specs.get('appname', '')

# 抄paramiko的demo的interative shell
def interactive_shell(chan):
    import select
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)

        while True:
            r, _, _ = select.select([chan, sys.stdin], [], [])
            if chan in r:
                try:
                    x = u(chan.recv(1024))
                    if len(x) == 0:
                        sys.stdout.write('\r\n*** EOF\r\n')
                        break
                    sys.stdout.write(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass
            if sys.stdin in r:
                x = sys.stdin.read(1)
                if len(x) == 0:
                    break
                chan.send(x)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
