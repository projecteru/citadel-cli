# coding: utf-8

import click
import yaml
from prettytable import PrettyTable

from corecli.cli.utils import handle_core_error, error, info


def _container_table(containers):
    table = PrettyTable(['name', 'id', 'nodename', 'podname', 'appname', 'sha', 'entrypoint', 'env', 'cpu', 'ip'])
    for c in containers:
        try:
            networks = c['info']['NetworkSettings']['Networks']
        except KeyError:
            networks = {}

        ns = ['%s:%s' % (name, network['IPAddress']) for name, network in networks.iteritems()]
        table.add_row([c['name'], c['container_id'], c['nodename'], c['podname'], c['appname'], c['sha'][:7], c['entrypoint'], c['env'], c['cpu_quota'], ','.join(ns)])
    return table


@click.argument('appname')
@click.pass_context
@handle_core_error
def get_app(ctx, appname):
    core = ctx.obj['coreapi']
    app = core.get_app(appname)

    table = PrettyTable(['name', 'git', 'created'])
    table.align['git'] = 'l'
    table.add_row([app['name'], app['git'], app['created']])
    click.echo(table)


@click.argument('appname')
@click.pass_context
@handle_core_error
def get_app_envs(ctx, appname):
    core = ctx.obj['coreapi']
    envs = core.get_app_envs(appname)

    table = PrettyTable(['name'])
    table.align['name'] = 'l'

    for env in envs:
        table.add_row([env['envname']])
    click.echo(table)


@click.argument('action')
@click.argument('appname')
@click.argument('envname')
@click.argument('envvars', nargs=-1)
@click.pass_context
@handle_core_error
def app_env(ctx, action, appname, envname, envvars):
    core = ctx.obj['coreapi']

    if action == 'get':
        env = core.get_app_env(appname, envname)

        table = PrettyTable(['key', 'value'])
        table.align['value'] = 'l'

        for key, value in env['vars'].iteritems():
            table.add_row([key, value])
        click.echo(table)
        return

    if action == 'set':
        kv = {}
        for v in envvars:
            if '=' not in v:
                click.echo(error('Env var must be like key=value'))
                ctx.exit(-1)
            key, value = v.split('=', 1)
            kv[key] = value

        core.set_app_env(appname, envname, **kv)
        click.echo(info('Set environment variables for %s %s done' % (appname, envname)))
        return

    if action in ('delete', 'remove'):
        core.delete_app_env(appname, envname)
        click.echo(info('Delete environment variables for %s %s done' % (appname, envname)))
        return

    click.echo(error('ACTION must be in "get" / "set" / "delete" / "remove".'))


@click.argument('appname')
@click.pass_context
@handle_core_error
def get_app_containers(ctx, appname):
    core = ctx.obj['coreapi']
    containers = core.get_app_containers(appname)
    click.echo(_container_table(containers))


@click.argument('appname')
@click.pass_context
@handle_core_error
def get_app_releases(ctx, appname):
    core = ctx.obj['coreapi']
    releases = core.get_app_releases(appname)

    table = PrettyTable(['name', 'sha', 'image', 'created'])
    for r in releases:
        table.add_row([appname, r['sha'], r['image'], r['created']])
    click.echo(table)


@click.argument('appname')
@click.argument('sha')
@click.pass_context
@handle_core_error
def get_release(ctx, appname, sha):
    core = ctx.obj['coreapi']
    r = core.get_release(appname, sha)

    table = PrettyTable(['name', 'sha', 'image', 'created'])
    table.add_row([appname, r['sha'], r['image'], r['created']])
    click.echo(table)


@click.argument('appname')
@click.argument('sha')
@click.pass_context
@handle_core_error
def get_release_specs(ctx, appname, sha):
    core = ctx.obj['coreapi']
    release = core.get_release(appname, sha)
    click.echo(yaml.safe_dump(release['specs'], default_flow_style=False))


@click.argument('appname')
@click.argument('sha')
@click.pass_context
@handle_core_error
def get_release_containers(ctx, appname, sha):
    core = ctx.obj['coreapi']
    containers = core.get_release_containers(appname, sha)
    click.echo(_container_table(containers))


@click.argument('appname')
@click.argument('sha')
@click.argument('git')
@click.pass_context
@handle_core_error
def register_release(ctx, appname, sha, git):
    core = ctx.obj['coreapi']
    core.register_release(appname, sha, git)
    click.echo(info('Register %s %s %s done.' % (appname, sha, git)))
