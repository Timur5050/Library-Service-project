from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create a superuser programmatically"

    def handle(self, *args, **kwargs):
        email = "admin@example.com"
        password = "12345678"

        User = get_user_model()
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{email}" created successfully'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser "{email}" already exists'))
