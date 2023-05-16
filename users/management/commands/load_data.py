from django.core.management.base import BaseCommand
from users.models import User, UserProfile

class Command(BaseCommand):

    def handle(self, *args, **options):
        table_name = "User"
        user = User.objects.create(
            email="admin@email.com",
            phone_number="+923321234567",
            fullname="Admin",
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        user.set_password(("admin123!@#"))
        user.save()
        self.stdout.write(
            self.style.SUCCESS(f"Data migration for ' {table_name} ' ran successfully!")
        )

        table_name = "UserProfile"
        user_profile = UserProfile.objects.create(user = user, city = "Peshawar")
        self.stdout.write(
            self.style.SUCCESS(f"Data migration for ' {table_name} ' ran successfully!")
        )
