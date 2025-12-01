from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


class Platform(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, platform, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        if not platform:
            raise ValueError(_("The Platform field must be set"))

        email = self.normalize_email(email)
        # Generate unique username
        username = f"{email}@{platform.id}"
        user = self.model(email=email, platform=platform, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Superusers are not bound to a specific platform logic in this
        # simple implementation, but we need to satisfy the model requirements.
        # For simplicity, we create a default "Admin" platform if it doesn't exist.
        # Note: In a real multi-tenant system, superusers might be global.
        # Here we just make it work for Django Admin.
        platform, _ = Platform.objects.get_or_create(name="Admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, platform, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"))
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name="users"
    )
    # Unique identifier combining email and platform
    username = models.CharField(max_length=255, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        unique_together = [["email", "platform"]]

    def save(self, *args, **kwargs):
        # Generate unique username from email and platform
        if not self.username:
            self.username = f"{self.email}@{self.platform_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.platform.name})"


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, related_name="devices"
    )
    name = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.user.email}"
