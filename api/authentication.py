from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken


class PlatformJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that validates the token's platform claim
    against the user's platform.
    """

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        # Enforce platform isolation
        # The token must have a platform_id claim
        platform_id = validated_token.get("platform_id")
        if not platform_id:
            raise InvalidToken(_("Token contains no platform claim"))

        user = self.get_user(validated_token)

        # Verify the user belongs to the platform in the token
        if user.platform_id != platform_id:
            raise AuthenticationFailed(_("User does not belong to the token platform"))

        # Attach platform to request for easy access in views
        request.platform_id = platform_id

        return user, validated_token
