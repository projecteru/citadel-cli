# coding: utf-8
import os

import click
from citadelpy import CoreAPIError

from corecli.cli.utils import (
    error, info, handle_core_error,
    get_commit_hash, get_remote_url,
)


def _get_repo(repo):
    ctx = click.get_current_context()
    repo = repo or get_remote_url(remote=ctx.obj['remotename'])
    if not repo:
        click.echo(error('repository is not set, check repository or pass argument'))
        ctx.exit(-1)
    return repo


def _get_sha(sha):
    sha = sha or get_commit_hash()
    if not sha:
        click.echo(error('commit hash not found, check repository or pass argument'))
        ctx = click.get_current_context()
        ctx.exit(-1)
    return sha


@click.argument('repo', required=False)
@click.argument('sha', required=False)
@click.option('--artifact', default='', help='artifact url to use')
@click.option('--uid', default='', help='uid of user inside container image')
@click.option('--with-artifacts', default=False, help='automatically detect gitlab artifacts file to upload', is_flag=True)
@click.pass_context
def build(ctx, repo, sha, artifact, uid, with_artifacts):
    repo = _get_repo(repo)
    sha = _get_sha(sha)

    gitlab_build_id = ''
    if os.getenv('GITLAB_CI', '') and with_artifacts:
        gitlab_build_id = os.getenv('CI_BUILD_ID', '')

    core = ctx.obj['coreapi']
    try:
        ms = core.build(repo, sha, artifact, uid, gitlab_build_id=gitlab_build_id)
    except CoreAPIError as e:
        if 'not found' in str(e).lower():
            click.echo(error(str(e)))
            ctx.exit()

    for m in ms:
        if m['error']:
            if 'not found' in m['error'].lower():
                click.echo(error(m['error']))
                ctx.exit()
            else:
                click.echo(error(m['error']), nl=False)
                ctx.exit(-1)
        if m['stream']:
            click.echo(m['stream'], nl=False)
        if m['status']:
            click.echo(info(m['status']))
            if m['progress']:
                click.echo(m['progress'])

    click.echo(info('Build %s %s done.' % (repo, sha)))


@click.argument('podname')
@click.argument('entrypoint')
@click.option('--repo', default='', help='git repository url, default is from `git remote get-url origin`')
@click.option('--sha', default='', help='git commit hash, default is from `git rev-parse HEAD`')
@click.option('--cpu', default=0, type=float, help='how many CPUs to set, e.g. --cpu 1.5')
@click.option('--memory', default=536870912, type=float, help='how much memory to set, e.g. --memory 536870912')
@click.option('--count', default=1, type=int, help='how many containers to deploy, e.g. --count 2')
@click.option('--networks', default='', help='networks to bind, NetworkName:IP, e.g. --networks network:10.102.0.37 --networks network', multiple=True)
@click.option('--nodename', default='', help='nodename to deploy, e.g. --nodename zzz1')
@click.option('--envname', default='', help='envname to use')
@click.option('--extraenv', default='', help='extra environment variables, e.g. --extraenv KEY1=VALUE1 --extraenv KEY2=VALUE2', multiple=True)
@click.pass_context
@handle_core_error
def deploy(ctx, podname, entrypoint, repo, sha, cpu, memory, count, networks, nodename, envname, extraenv):

    def _networks_dict(networks):
        ns = []
        for n in networks:
            ps = n.split(':', 1)
            if len(ps) == 1:
                ps.append('')
            ns.append(ps)
        return dict(ns)

    networks = _networks_dict(networks)
    repo = _get_repo(repo)
    sha = _get_sha(sha)

    core = ctx.obj['coreapi']
    for m in core.deploy(repo, sha, podname, nodename, entrypoint, cpu, memory, count, networks, envname, extraenv):
        if not m['success']:
            click.echo(error(m['error']))
        else:
            click.echo(info('Container %s / %s created successfully' % (m['id'], m['name'])))


@click.argument('ids', nargs=-1)
@click.pass_context
@handle_core_error
def remove(ctx, ids):
    if not ids:
        click.echo(error('No ids given'))
        ctx.exit(-1)

    core = ctx.obj['coreapi']
    for m in core.remove(ids):
        if m['success']:
            click.echo(info('Container %s removed successfully' % m['id']))
        else:
            click.echo(error('Fail to remove %s, error: %s' % (m['id'], m['message'])))


@click.argument('ids', nargs=-1)
@click.option('--repo', default='', help='git repository url, default is from `git remote get-url origin`')
@click.option('--sha', default='', help='git commit hash, default is from `git rev-parse HEAD`')
@click.pass_context
@handle_core_error
def upgrade(ctx, ids, repo, sha):
    if not ids:
        click.echo(error('No ids given'))
        ctx.exit(-1)

    repo = _get_repo(repo)
    sha = _get_sha(sha)

    core = ctx.obj['coreapi']
    for m in core.upgrade(ids, repo, sha):
        if m['success']:
            click.echo(info('Container %s upgrade to %s / %s successfully' % (m['id'], m['new_id'], m['new_name'])))
        else:
            click.echo(error('Fail to upgrade %s, error: %s' % (m['id'], m['error'])))


@click.argument('nodename')
@click.argument('appname')
@click.pass_context
@handle_core_error
def log(ctx, nodename, appname):
    core = ctx.obj['coreapi']
    logs = core.log(nodename, appname)

    if logs is None:
        click.echo(error('wrong nodename %s' % nodename))
        ctx.exit(-1)

    for m in logs:
        click.echo('[%s, %s, %s, %s, %s] %s' % (m['datetime'], m['type'], m['entrypoint'], m['id'][:7], m['ident'], m['data']))
