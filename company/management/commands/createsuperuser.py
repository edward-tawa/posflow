from django.core.management.base import BaseCommand
from getpass import getpass
from company.models import Company
from branch.models import Branch


class Command(BaseCommand):
    help = "Create a superuser with an initial branch"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Creating superuser..."))

        # 1. Prompt for company info
        email = input("Email: ").strip()
        name = input("Name: ").strip()

        # 2. Prompt for password securely
        while True:
            password = getpass("Password: ")
            password2 = getpass("Password (again): ")
            if password != password2:
                self.stdout.write(self.style.ERROR("Passwords do not match. Try again."))
                continue
            if len(password) < 8:
                self.stdout.write(self.style.ERROR("Password too short (min 8 characters)."))
                continue
            break

        # 3. Prompt for branch info
        branch_name = input("Branch Name: ").strip()
        branch_address = input("Branch Address: ").strip()

        # 4. Create superuser
        company = Company.objects.create_superuser(
            name=name,
            email=email,
            password=password,
            branch_name=branch_name,
            branch_address=branch_address
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Superuser '{email}' created with branch '{branch_name}'."
            )
        )
