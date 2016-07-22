# coding: utf-8

class MimironMixin(object):

    def get_mimiron_container_info(self, username):
        return self._do('/mimiron/container/{}'.format(username))
