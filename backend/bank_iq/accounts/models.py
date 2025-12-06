from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.helpers.minio import get_s3_storage
from core.helpers.profile_db_functions import user_avatar_upload_path


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True,
                              blank=False,
                              null=False,
                              max_length=254,
                              error_messages={'unique': _('A user with that email already exists')})

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.username or self.email


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to=user_avatar_upload_path, null=True, blank=True, storage=get_s3_storage())

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Profile of {self.user.username}'
