# coding: utf-8

class MimironMixin(object):

    def get_mimiron_container_info(self, username):
        return self._do('/mimiron/container/{}'.format(username))

    def get_mimiron_auth_info(self):
        return self.username, self.auth_token
