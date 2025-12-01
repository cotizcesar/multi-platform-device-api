from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Device
from .permissions import IsSamePlatform
from .serializers import DeviceSerializer, PlatformTokenObtainPairSerializer


class PlatformTokenObtainPairView(TokenObtainPairView):
    serializer_class = PlatformTokenObtainPairSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated, IsSamePlatform]

    def get_queryset(self):
        """
        This view should return a list of all the devices
        for the currently authenticated user and their platform.
        """
        user = self.request.user
        # Filter by user AND platform (though user implies platform in our model,
        # explicit filtering is safer and clearer)
        return Device.objects.filter(user=user, platform=user.platform)

    def perform_create(self, serializer):
        # The serializer create method already handles user/platform assignment
        # via context['request'].user, but we can double check or just save.
        serializer.save()
