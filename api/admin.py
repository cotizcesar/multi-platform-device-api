from django.contrib import admin

from .models import Device, Platform, User


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "platform", "is_active", "is_staff", "created_at"]
    list_filter = ["platform", "is_active", "is_staff"]
    search_fields = ["email"]
    readonly_fields = ["created_at"]


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "platform", "ip_address", "is_active", "created_at"]
    list_filter = ["platform", "is_active"]
    search_fields = ["name", "user__email", "ip_address"]
    readonly_fields = ["created_at", "updated_at"]
