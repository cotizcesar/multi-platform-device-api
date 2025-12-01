from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api.models import Device, Platform, User


class MultiPlatformTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Platforms
        self.platform_android = Platform.objects.create(name="Android")
        self.platform_ios = Platform.objects.create(name="iOS")

        # Create Users with same email but different platforms
        self.email = "test@example.com"
        self.password = "testpass123"

        self.user_android = User.objects.create_user(
            email=self.email, platform=self.platform_android, password=self.password
        )

        self.user_ios = User.objects.create_user(
            email=self.email, platform=self.platform_ios, password=self.password
        )

        # Create Devices
        self.device_android = Device.objects.create(
            user=self.user_android,
            platform=self.platform_android,
            name="Pixel 6",
            ip_address="192.168.1.10",
            is_active=True,
        )

        self.device_ios = Device.objects.create(
            user=self.user_ios,
            platform=self.platform_ios,
            name="iPhone 13",
            ip_address="192.168.1.20",
            is_active=True,
        )

    def test_login_android(self):
        """Test login on Android platform"""
        url = reverse("token_obtain_pair")
        data = {"email": self.email, "password": self.password, "platform": "Android"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        # Verify token works for Android devices
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        devices_url = reverse("device-list")
        response = self.client.get(devices_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Pixel 6")

    def test_login_ios(self):
        """Test login on iOS platform"""
        url = reverse("token_obtain_pair")
        data = {"email": self.email, "password": self.password, "platform": "iOS"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify token works for iOS devices
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        devices_url = reverse("device-list")
        response = self.client.get(devices_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "iPhone 13")

    def test_platform_isolation(self):
        """Test that Android token cannot see iOS devices"""
        # Login as Android
        url = reverse("token_obtain_pair")
        data = {"email": self.email, "password": self.password, "platform": "Android"}
        response = self.client.post(url, data, format="json")
        access_token = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        # Try to access iOS device directly (if we knew the ID)
        # Note: In a real scenario, IDs might be UUIDs to prevent guessing,
        # but here we rely on the queryset filtering.

        # 1. List should only show Android devices
        devices_url = reverse("device-list")
        response = self.client.get(devices_url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Pixel 6")

        # 2. Try to access iOS device detail
        ios_device_url = reverse("device-detail", args=[self.device_ios.id])
        response = self.client.get(ios_device_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_login(self):
        """Test login with wrong platform"""
        url = reverse("token_obtain_pair")
        data = {
            "email": self.email,
            "password": self.password,
            "platform": "WindowsPhone",  # Doesn't exist
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_device(self):
        """Test creating a device automatically assigns user and platform"""
        # Login as Android
        url = reverse("token_obtain_pair")
        data = {"email": self.email, "password": self.password, "platform": "Android"}
        response = self.client.post(url, data, format="json")
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token)

        # Create new device
        devices_url = reverse("device-list")
        new_device_data = {
            "name": "New Android Tablet",
            "ip_address": "10.0.0.99",
            "is_active": True,
        }
        response = self.client.post(devices_url, new_device_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify it was assigned to the correct user and platform
        device_id = response.data["id"]
        device = Device.objects.get(id=device_id)
        self.assertEqual(device.user, self.user_android)
        self.assertEqual(device.platform, self.platform_android)
