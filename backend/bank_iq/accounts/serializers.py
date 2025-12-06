import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Profile
from .utils import generate_username_from_names


User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = ("image_url",)

    def get_image_url(self, obj) -> str | None:
        if not obj or not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "is_staff", "is_superuser", "profile")
        read_only_fields = ("is_staff", "is_superuser", "id")


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True,
                                     validators=(
                                         UniqueValidator(queryset=User.objects.all(),
                                                         message="Пользователь с таким username уже существует"),))
    email = serializers.CharField(required=True,
                                  validators=(UniqueValidator(queryset=User.objects.all(),
                                                              message="Пользователь с таким email уже существует"),))
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password")

    def create(self, validated_data):
        username = validated_data.get("username")
        first_name = validated_data.get("first_name", "") or ""
        last_name = validated_data.get("last_name", "") or ""
        email = validated_data.get("email", "")

        if not username:
            username = generate_username_from_names(first_name, last_name)

        user = User(username=username, email=email, first_name=first_name, last_name=last_name)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def to_representation(self, instance):
        """
        Когда сериализатор используется для вывода (serializer.data),
        возвращаем полную информацию о созданном пользователе через UserSerializer,
        чтобы там присутствовал profile.image_url.
        """
        return UserSerializer(instance, context=self.context).data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user_data = UserSerializer(self.user, context=self.context).data
        data.update({"user": user_data})
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class PublicUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name", "profile")


class UpdateUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    photo = serializers.ImageField(required=False, allow_null=True,
                                   style={'input_type': 'file', 'base_template': 'file.html'})

    def update(self, instance, validated_data):
        """
        instance: user instance
        validated_data: dict with optional first_name, last_name, photo
        """
        logger = logging.getLogger(__name__)
        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")
        photo = validated_data.get("photo", None)

        if first_name is not None:
            instance.first_name = first_name
        if last_name is not None:
            instance.last_name = last_name

        with transaction.atomic():
            instance.save()

            profile, _ = Profile.objects.get_or_create(user=instance)

            if photo is not None:
                try:
                    if profile.image:
                        profile.image.delete(save=False)
                    profile.image = photo
                    profile.save(update_fields=["image"])
                except Exception as exc:
                    logger.exception("Failed to save profile.image for user %s: %s", instance.pk, exc)
        return instance

    def to_representation(self, instance):
        return PublicUserSerializer(instance, context=self.context).data
