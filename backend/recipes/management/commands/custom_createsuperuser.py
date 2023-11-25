from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Creates a superuser"

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                "admin",
                "admin@admin.com",
                "secret_password"
            )
            self.stdout.write(
                self.style.SUCCESS("Successfully created a new superuser")
            )
        else:
            self.stdout.write(self.style.WARNING("Superuser already exists"))
