# coding: utf-8

class NetworkMixin(object):

    def get_networks(self):
        return self._do('/network')
