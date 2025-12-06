import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from core.helpers.profile_db_functions import generate_gravatar_avatar
from .models import Profile


User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        avatar_key = generate_gravatar_avatar(instance)
        if avatar_key:
            profile.image.name = avatar_key
            profile.save()
    else:
        Profile.objects.get_or_create(user=instance)


@receiver(pre_delete, sender=Profile)
def delete_profile_image(sender, instance, **kwargs):
    if instance.image:
        storage = instance.image.storage
        name = instance.image.name
        try:
            storage.delete(name)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning("Failed to delete file from S3: %s — %s", name, e)
