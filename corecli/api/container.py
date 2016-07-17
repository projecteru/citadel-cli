# coding: utf-8

class ContainerMixin(object):

    def get_container(self, container_id):
        return self._do('/container/%s' % container_id)
