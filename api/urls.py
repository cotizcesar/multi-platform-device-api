from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import DeviceViewSet, PlatformTokenObtainPairView

router = DefaultRouter()
router.register(r"devices", DeviceViewSet, basename="device")

urlpatterns = [
    path(
        "auth/login/", PlatformTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
