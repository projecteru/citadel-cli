# coding: utf-8

import click
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
