# coding: utf-8

import os
import yaml
import click
import envoy
from functools import wraps
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
