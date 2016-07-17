# coding: utf-8

import click

from corecli.cli.utils import handle_core_error, error, info


@click.argument('repo')
@click.argument('sha')
@click.option('--artifact', default='')
@click.option('--uid', default='')
@click.pass_context
@handle_core_error
def build(ctx, repo, sha, artifact, uid):
    core = ctx.obj['coreapi']
    for m in core.build(repo, sha, artifact, uid):
        if m['error']:
            click.echo(error(m['error']), nl=False)
        if m['stream']:
            click.echo(m['stream'], nl=False)
        if m['status']:
            click.echo(info(m['status']))
            if m['progress']:
                click.echo(m['progress'])

    click.echo(info('Build %s %s done.' % (repo, sha)))
