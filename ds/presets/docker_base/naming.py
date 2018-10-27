from __future__ import unicode_literals

from ds import context


class ContainerNaming(context.Context):
    def check(self):
        super(ContainerNaming, self).check()
        assert (self.has_container_name and self.container_name), \
            'Container name is not defined'

    @property
    def has_container_name(self):
        return hasattr(self, 'container_name')

    @property
    def has_image_name(self):
        return hasattr(self, 'image_name')


class ImageNaming(ContainerNaming):
    def check(self):
        super(ImageNaming, self).check()
        assert (self.has_image_name and self.image_name), \
            'Image name is not defined'


class DefaultNaming(ImageNaming, ContainerNaming):
    @property
    def container_name(self):
        if not self.image_name:
            return
        image = self.image_name.split(':', 1)[0]
        return '--'.join([self.project_name, image])
