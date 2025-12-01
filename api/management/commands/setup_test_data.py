from django.core.management.base import BaseCommand

from api.models import Device, Platform, User


class Command(BaseCommand):
    help = "Creates test data: Platforms, Users, and Devices"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating test data...")

        # Create Platforms
        platforms = ["Android", "iOS", "Web"]
        platform_objs = {}
        for p_name in platforms:
            p, created = Platform.objects.get_or_create(name=p_name)
            platform_objs[p_name] = p
            if created:
                self.stdout.write(f"Created platform: {p_name}")

        # Create Users (same email, different platforms)
        email = "user@example.com"
        password = "password123"

        for p_name, p_obj in platform_objs.items():
            if not User.objects.filter(email=email, platform=p_obj).exists():
                user = User.objects.create_user(
                    email=email, platform=p_obj, password=password
                )
                self.stdout.write(f"Created user: {email} on {p_name}")

                # Create Devices for this user
                Device.objects.create(
                    user=user,
                    platform=p_obj,
                    name=f"{p_name} Device 1",
                    ip_address="192.168.1.101",
                    is_active=True,
                )
                Device.objects.create(
                    user=user,
                    platform=p_obj,
                    name=f"{p_name} Device 2",
                    ip_address="10.0.0.5",
                    is_active=False,
                )
                self.stdout.write(f"Created devices for user on {p_name}")

        self.stdout.write(self.style.SUCCESS("Successfully created test data"))
