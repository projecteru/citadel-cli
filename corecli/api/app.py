# coding: utf-8

class AppMixin(object):

    def get_app(self, appname):
        return self._do('/app/%s' % appname)

    def get_app_containers(self, appname, start=0, limit=20):
        params = {'start': start, 'limit': limit}
        return self._do('/app/%s/containers' % appname, params=params)

    def get_app_releases(self, appname, start=0, limit=20):
        params = {'start': start, 'limit': limit}
        return self._do('/app/%s/releases' % appname, params=params)

    def get_app_envs(self, appname):
        return self._do('/app/%s/env' % appname)

    def get_app_env(self, appname, envname):
        return self._do('/app/%s/env/%s' % (appname, envname))

    def set_app_env(self, appname, envname, **kwargs):
        return self._do('/app/%s/env/%s' % (appname, envname), method='PUT', json=kwargs)

    def delete_app_env(self, appname, envname):
        return self._do('/app/%s/env/%s' % (appname, envname), method='DELETE')

    def get_release(self, appname, sha):
        return self._do('/app/%s/version/%s' % (appname, sha))

    def get_release_containers(self, appname, sha, start=0, limit=20):
        params = {'start': start, 'limit': limit}
        return self._do('/app/%s/version/%s/containers' % (appname, sha), params=params)

    def register_release(self, appname, sha, git):
        data = {
            'name': appname,
            'sha': sha,
            'git': git,
        }
        return self._do('/app/register', method='POST', json=data)
