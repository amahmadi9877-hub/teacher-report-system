from django.core.management.base import BaseCommand, CommandError
from django.db import DataError, IntegrityError

from accounts.enums import UserRole
from accounts.models.user import User
from core.utils import required_input, get_password


class Command(BaseCommand):
    help = f"""create new user command
    use: ./manage.py create_user <roll: {[value for value in UserRole.selectable_choices()]}>"""

    def add_arguments(self, parser):
        parser.add_argument(
            "role",
            choices=[value for value in UserRole.selectable_choices()],
        )

    def handle(self, *args, **options):
        username = required_input("Username: ")
        first_name = required_input("Firstname: ")
        last_name = required_input("Lastname: ")
        phone_number = required_input("PhoneNumber: ")
        backup_phone_number = (
            required_input("Backup PhoneNumber: ")
            if options["role"] == UserRole.TEACHER
            else input("Backup PhoneNumber: ")
        )
        password = get_password("Password: ")
        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=options["role"],
            phone_number=phone_number,
            backup_phone_number=backup_phone_number,
        )
        user.set_password(password)
        try:
            user.save()
        except IntegrityError as i:
            raise CommandError(str(i))
        except DataError as d:
            raise CommandError(str(d))

        self.stdout.write(
            self.style.SUCCESS(f'User "{user.username}" created successfully.')
        )
