from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Command(BaseCommand):
    """command to create a platform admin user
    """

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = "platformadmin"
        email = "palatform_admin@gmail.com"
        password = "admin123"

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, email=email, password=password)
            group, _ = Group.objects.get_or_create(name='platform_admin')
            user.groups.add(group)
            self.stdout.write(self.style.SUCCESS(f"Platform admin '{username}' created and added to group."))
        else:
            self.stdout.write("User already exists.")
