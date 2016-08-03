# coding: utf-8

class ActionMixin(object):

    def build(self, repo, sha, artifact='', uid=''):
        """把一个仓库打包成可以部署的镜像.
        repo: 仓库地址, 如git@github.com:name/project.git.
        sha: 要打包的版本号, git sha值.
        artifact: 一些可能需要的其他文件, 是一个URL, 例如 gitlab.com/api/v3/project/:name/build/:build/artifacts.
        uid: 镜像内部对应的用户的uid, 不传的话默认使用app的id.
        """
        data = {'repo': repo, 'sha': sha, 'artifact': artifact, 'uid': uid}
        return self._do_stream('/build', method='POST', json=data)

    def deploy(self, repo, sha, podname, nodename, entrypoint, cpu_quota, count, networks=None, envname=None, extra_env=None):
        """部署一个仓库.
        repo: 仓库地址, 如git@github.com:name/project.git.
        sha: 要部署的版本号, git sha值.
        podname: 要部署的区域, 例如dev, 或者nova.
        entrypoint: 对应app.yaml里的entrypoints的名字.
        cpu_quota: 需要的cpu个数, 例如1, 或者1.5, 如果是public的部署, 传0.
        networks: 要绑定的网络, 例如{'10.102.0.0/16': '10.102.2.37'}, key是CIDR, value是IP.
                  意思是绑定CIDR里的这个IP. 如果随机选择不指定IP, IP传空字符串''.
        envname: 要注入的一组环境变量的名字, 例如dev, 会把名字为dev的这一组环境变量注入容器.
        extra_env: 额外需要注入的环境变量, 格式是['ENV_NAME1=value1', 'ENV_NAME2=key2=value2'].
        """
        data = {}
        data['repo'] = repo
        data['sha'] = sha
        data['podname'] = podname
        data['nodename'] = nodename
        data['entrypoint'] = entrypoint
        data['cpu_quota'] = cpu_quota
        data['count'] = count
        if networks and isinstance(networks, dict):
            data['networks'] = networks
        if envname:
            data['envname'] = envname
        if extra_env and isinstance(extra_env, list):
            data['extra_env'] = extra_env
        return self._do_stream('/deploy', method='POST', json=data)

    def remove(self, ids):
        """删除这些容器.
        ids: 容器ID, 需要填写完整的64个字符的字符串ID, 是一个list.
        """
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        data = {'ids': ids}
        return self._do_stream('/remove', method='POST', json=data)

    def upgrade(self, ids, repo, sha):
        """更新这些容器. 把ids的容器按照原来的规格部署, 但是镜像替换成repo+sha组合确定的镜像.
        ids: 容器ID, 需要填写完整的64个字符的字符串ID, 是一个list.
        repo: 仓库地址, 如git@github.com:name/project.git.
        sha: 要打包的版本号, git sha值.
        """
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        data = {'ids': ids, 'repo': repo, 'sha': sha}
        return self._do_stream('/upgrade', method='POST', json=data)

    def log(self, nodename, appname):
        """走agent拿nodename的appname"""
        nodenames = {}
        for p in self.get_pods():
            for n in self.get_pod_nodes(p['name']):
                nodenames[n['name']] = p['name']
        podname = nodenames.get(nodename, '')
        if not podname:
            return None

        data = {'appname': appname, 'podname': podname, 'nodename': nodename}
        return self._do_stream('/log', method='POST', json=data)
