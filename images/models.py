from django.db.models.signals import pre_delete
from django.dispatch import receiver
from wagtail.wagtailimages.models import Image, AbstractImage, AbstractRendition
from django.db import models

class SnipImage(AbstractImage):
    caption = models.CharField(max_length=65, blank=True)
    admin_form_fields = Image.admin_form_fields + ('caption',)

class SnipImageRendition(AbstractRendition):
    image = models.ForeignKey(SnipImage, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )


# Delete the source image file when an image is deleted
@receiver(pre_delete, sender=SnipImage)
def image_delete(sender, instance, **kwargs):
    instance.file.delete(False)


# Delete the rendition image file when a rendition is deleted
@receiver(pre_delete, sender=SnipImageRendition)
def rendition_delete(sender, instance, **kwargs):
    instance.file.delete(False)