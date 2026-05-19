import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import django_rq
from .models import Video
from .tasks import convert_video_resolution


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_video_resolution, instance.video_file.path)


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding 'Video' object ist deleted.
    """
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)