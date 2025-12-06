from django.contrib import admin
from django.utils.html import format_html

from .models import CustomUser, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    readonly_fields = ("image_tag",)

    def get_actions(self, request):
        actions = super().get_actions(request) or {}
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def image_tag(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="80" />')
        return "-"

    image_tag.short_description = "Avatar"


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name", "is_staff", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_active", "is_superuser")
    list_display_links = ("id", "username", "email")
