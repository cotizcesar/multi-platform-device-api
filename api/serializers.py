from rest_framework import serializers
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Device, Platform, User


class PlatformTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to handle login with email + password + platform.
    """

    email = serializers.EmailField(required=True)
    platform = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the default username field
        if self.username_field in self.fields:
            del self.fields[self.username_field]

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        platform_name = attrs.get("platform")

        if email and password and platform_name:
            # Find the platform first
            try:
                platform = Platform.objects.get(name=platform_name)
            except Platform.DoesNotExist:
                raise AuthenticationFailed(
                    "Platform not found", code="no_active_account"
                ) from None

            # Authenticate using the custom backend logic or manual check
            # Since Django's authenticate() usually takes username/password,
            # and our user is unique by email+platform, we need to find the
            # specific user first.

            try:
                user = User.objects.get(email=email, platform=platform)
            except User.DoesNotExist:
                raise AuthenticationFailed(
                    "No active account found with the given credentials",
                    code="no_active_account",
                ) from None

            if not user.check_password(password):
                raise AuthenticationFailed(
                    "No active account found with the given credentials",
                    code="no_active_account",
                )

            if not user.is_active:
                raise AuthenticationFailed("User is inactive", code="no_active_account")

            self.user = user
        else:
            raise AuthenticationFailed(
                'Must include "email", "password", and "platform".'
            )

        # Generate tokens manually
        refresh = self.get_token(user)

        # Add platform_id to both tokens
        refresh["platform_id"] = user.platform_id
        
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id,
            "email": user.email,
            "platform": user.platform.name,
        }

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["platform_id"] = user.platform_id
        return token


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ["id", "name", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "platform", "is_active", "created_at"]
        read_only_fields = ["platform"]


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id", "name", "ip_address", "is_active", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        # Automatically associate with the current user and their platform
        user = self.context["request"].user
        validated_data["user"] = user
        validated_data["platform"] = user.platform
        return super().create(validated_data)
