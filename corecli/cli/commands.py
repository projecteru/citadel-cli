# coding: utf-8

from corecli.cli.app import (
    get_app,
    get_app_releases,
    get_app_containers,
    get_app_envs,
    app_env,
    get_release,
    get_release_specs,
    get_release_containers,
    register_release,
)
from corecli.cli.action import (
    build,
)


commands = {
    'app:get': get_app,
    'app:envs': get_app_envs,
    'app:env': app_env,
    'app:release': get_app_releases,
    'app:container': get_app_containers,

    'release:get': get_release,
    'release:specs': get_release_specs,
    'release:container': get_release_containers,

    'register': register_release,
    'build': build,
}
