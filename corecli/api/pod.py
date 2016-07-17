# coding: utf-8

class PodMixin(object):

    def get_pods(self):
        return self._do('/pod')

    def get_pod(self, podname):
        return self._do('/pod/%s' % podname)

    def get_pod_nodes(self, podname):
        return self._do('/pod/%s/nodes' % podname)

    def get_pod_containers(self, podname, start=0, limit=20):
        params = {'start': start, 'limit': limit}
        return self._do('/pod/%s/containers' % podname, params=params)
