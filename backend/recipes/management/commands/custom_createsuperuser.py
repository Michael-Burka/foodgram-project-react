import os
from dotenv import load_dotenv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

current_directory = Path(__file__).parent
env_path = current_directory.parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Command(BaseCommand):
    help = "Creates a superuser"

    def handle(self, *args, **options):
        User = get_user_model()

        superuser_password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if superuser_password:
            if not User.objects.filter(username="admin").exists():
                User.objects.create_superuser(
                    "admin",
                    "admin@admin.com",
                    superuser_password
                )
                self.stdout.write(
                    self.style.SUCCESS("Successfully created a new superuser")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("Superuser already exists")
                )
        else:
            self.stdout.write(
                self.style.ERROR(
                    "Superuser creation skipped: No DJANGO_SUPERUSER_PASSWORD"
                    " provided in .env file")
            )
