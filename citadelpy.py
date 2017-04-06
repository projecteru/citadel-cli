# -*- coding: utf-8 -*-
import json as jsonlib
import logging

from requests import Session


logger = logging.getLogger(__name__)


class CoreAPIError(Exception):
    pass


class CoreAPI(object):

    def __init__(self, host, version='v1', timeout=None, password='', auth_token='', zone=None):
        self.zone = zone
        self.host = host
        self.version = version
        self.timeout = timeout
        self.auth_token = auth_token

        self.base = '%s/api/%s' % (self.host, version)
        self.session = Session()
        self.session.headers.update({'X-Neptulon-Token': auth_token})

    def request(self, path, method='GET', params=None, data=None, json=None, **kwargs):
        """Wrap around requests.request method"""
        url = self.base + path
        params = params or {}
        params['zone'] = self.zone
        resp = self.session.request(url=url,
                                    method=method,
                                    params=params,
                                    data=data,
                                    json=json,
                                    timeout=self.timeout,
                                    **kwargs)
        code = resp.status_code
        if code != 200:
            raise CoreAPIError('Citadel internal error: code {}, body {}'.format(code, resp.text))
        try:
            responson = resp.json()
        except ValueError:
            raise CoreAPIError('Citadel did not return json, code {}, body {}'.format(resp.status_code, resp.text))
        return responson

    def request_stream(self, path, method='GET', params=None, data=None, json=None, **kwargs):
        url = self.base + path
        params = params or {}
        params['zone'] = self.zone
        resp = self.session.request(url=url,
                                    method=method,
                                    params=params,
                                    data=data,
                                    json=json,
                                    timeout=self.timeout,
                                    stream=True)

        code = resp.status_code
        if code != 200:
            raise CoreAPIError('Citadel internal error: code {}, body {}'.format(code, resp.text))
        for line in resp.iter_lines():
            try:
                yield jsonlib.loads(line)
            except ValueError:
                raise CoreAPIError('Bad line interrupts stream response: {}'.format(line))

    def get_app(self, appname):
        return self.request('/app/%s' % appname)

    def get_app_containers(self, appname):
        return self.request('/app/%s/containers' % appname)

    def get_app_releases(self, appname):
        return self.request('/app/%s/releases' % appname)

    def get_app_envs(self, appname):
        return self.request('/app/%s/env' % appname)

    def get_app_env(self, appname, envname):
        return self.request('/app/%s/env/%s' % (appname, envname))

    def set_app_env(self, appname, envname, **kwargs):
        return self.request('/app/%s/env/%s' % (appname, envname), method='PUT', json=kwargs)

    def delete_app_env(self, appname, envname):
        return self.request('/app/%s/env/%s' % (appname, envname), method='DELETE')

    def get_release(self, appname, sha):
        return self.request('/app/%s/version/%s' % (appname, sha))

    def get_release_containers(self, appname, sha):
        return self.request('/app/%s/version/%s/containers' % (appname, sha))

    def register_release(self, appname, sha, git, branch=None):
        payload = {
            'name': appname,
            'sha': sha,
            'git': git,
            'branch': branch,
        }
        return self.request('/app/register', method='POST', json=payload)

    def get_container(self, container_id):
        return self.request('/container/%s' % container_id)

    def get_networks(self):
        raise NotImplementedError('/api/v1/network has been removed, please use /pod/[podname]/networks')

    def get_pod_networks(self, podname):
        return self.request('/pod/{}/networks'.format(podname))

    def get_pods(self):
        return self.request('/pod')

    def get_pod(self, podname):
        return self.request('/pod/%s' % podname)

    def get_pod_nodes(self, podname):
        return self.request('/pod/%s/nodes' % podname)

    def get_pod_containers(self, podname):
        return self.request('/pod/%s/containers' % podname)

    def get_memcap(self, podname):
        return self.request('/pod/%s/getmemcap' % podname)

    def sync_memcap(self, podname):
        return self.request('/pod/%s/syncmemcap' % podname, method='POST')

    def build(self, repo, sha, artifact='', uid='', **kwargs):
        """把一个仓库打包成可以部署的镜像.
        repo: 仓库地址, 如git@github.com:name/project.git.
        sha: 要打包的版本号, git sha值.
        artifact: 一些可能需要的其他文件, 是一个URL, 例如 gitlab.com/api/v3/project/:name/build/:build/artifacts.
        uid: 镜像内部对应的用户的uid, 不传的话默认使用app的id.
        """
        payload = {'repo': repo, 'sha': sha, 'artifact': artifact, 'uid': uid}
        payload.update(kwargs)
        return self.request_stream('/build', method='POST', json=payload)

    def deploy(self, repo, sha, podname, nodename, entrypoint, cpu_quota, memory, count, networks=None, envname=None, extra_env=None, **kwargs):
        """部署一个仓库.
        repo: 仓库地址, 如git@github.com:name/project.git.
        sha: 要部署的版本号, git sha值.
        podname: 要部署的区域, 例如dev, 或者nova.
        entrypoint: 对应app.yaml里的entrypoints的名字.
        cpu_quota: 需要的cpu个数, 例如1, 或者1.5, 如果是public的部署, 传0.
        memory: 最小4MB.
        networks: 要绑定的网络, 例如{'10.102.0.0/16': '10.102.2.37'}, key是CIDR, value是IP.
                  意思是绑定CIDR里的这个IP. 如果随机选择不指定IP, IP传空字符串''.
        envname: 要注入的一组环境变量的名字, 例如dev, 会把名字为dev的这一组环境变量注入容器.
        extra_env: 额外需要注入的环境变量, 格式是['ENV_NAME1=value1', 'ENV_NAME2=key2=value2'].
        """
        payload = {}
        payload['repo'] = repo
        payload['sha'] = sha
        payload['podname'] = podname
        payload['nodename'] = nodename
        payload['entrypoint'] = entrypoint
        payload['cpu_quota'] = cpu_quota
        payload['memory'] = memory
        payload['count'] = count
        if networks and isinstance(networks, dict):
            payload['networks'] = networks

        if envname:
            payload['envname'] = envname

        if extra_env and isinstance(extra_env, list):
            payload['extra_env'] = extra_env

        payload.update(kwargs)
        return self.request_stream('/deploy', method='POST', json=payload)

    def remove(self, ids, **kwargs):
        """删除这些容器.
        ids: 容器ID, 需要填写完整的64个字符的字符串ID, 是一个list.
        """
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        payload = {'ids': ids}
        payload.update(kwargs)
        return self.request_stream('/remove', method='POST', json=payload)

    def upgrade(self, ids, repo, sha, **kwargs):
        """更新这些容器. 把ids的容器按照原来的规格部署, 但是镜像替换成repo+sha组合确定的镜像.
        ids: 容器ID, 需要填写完整的64个字符的字符串ID, 是一个list.
        repo: 仓库地址, 如git@github.com:name/project.git.
        sha: 要打包的版本号, git sha值.
        """
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        payload = {'ids': ids, 'repo': repo, 'sha': sha}
        payload.update(kwargs)
        return self.request_stream('/upgrade', method='POST', json=payload)
