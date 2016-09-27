# coding: utf-8

import json
import re
import os
import select
import socket
import sys
import termios
import tty
from functools import wraps

import click
import envoy
import requests
import yaml
from citadelpy import CoreAPIError
from paramiko.py3compat import u


_GITLAB_CI_REMOTE_URL_PATTERN = re.compile(r'http://gitlab-ci-token:(\w+)@([\.\w]+)/([-\w]+)/([-\w]+).git')


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
    remote = r.std_out.strip()

    # 对gitlab ci需要特殊处理一下
    # 丫有个特殊的格式, 不太好支持...
    match = _GITLAB_CI_REMOTE_URL_PATTERN.match(remote)
    if match:
        host = match.group(1)
        group = match.group(2)
        project = match.group(3)
        return 'git@{host}:{group}/{project}.git'.format(host=host, group=group, project=project)
    return remote


def get_appname(cwd=None):
    try:
        with open(os.path.join(cwd or os.getcwd(), 'app.yaml'), 'r') as f:
            specs = yaml.load(f)
    except IOError:
        return ''
    return specs.get('appname', '')


def interactive_shell(chan):
    # 抄paramiko的demo的interative shell
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


def read_json_file(path):
    try:
        with open(path) as f:
            return json.loads(f.read())
    except (OSError, IOError):
        return None


def write_json_file(dic, path):
    with open(path, 'w') as f:
        f.write(json.dumps(dic))


def get_username(sso_url, token):
    req = sso_url.strip('/') + '/auth/profile' + '?token=' + token
    result = requests.get(req)
    if result.status_code != requests.codes.ok:
        result.raise_for_status()
    return result.json()['name']
