from rest_framework import permissions


class IsSamePlatform(permissions.BasePermission):
    """
    Custom permission to ensure the user can only access resources
    belonging to their platform.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the object has a platform attribute
        if hasattr(obj, "platform"):
            return obj.platform_id == request.user.platform_id
        return True
