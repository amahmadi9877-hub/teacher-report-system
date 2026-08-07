from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import DataError, IntegrityError
from accounts.enums import UserRole
from accounts.models.user import User
from core.utils import required_input, get_password

AUTH_USER = get_user_model()


class Command(BaseCommand):
    help = f"""create new user command
    use: ./manage.py create_user <roll: {[value for value in UserRole.selectable_choices()]}>"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--role",
            choices=[value for value in UserRole.selectable_choices()],
            required=True,
        )
        parser.add_argument("--username", required=True)
        parser.add_argument("--first-name", required=True)
        parser.add_argument("--last-name", required=True)
        parser.add_argument("--phone-number", required=True)
        parser.add_argument("--backup-phone-number", required=False)
        parser.add_argument("--password", required=True)

    def handle(self, *args, **options):
        if (
            not options.get("backup_phone_number")
            and options.get("role") == UserRole.TEACHER
        ):
            raise CommandError(
                "backup-phone-number is required for teachers!(--backup-phone-number)"
            )

        user = AUTH_USER(
            username=options.get("username"),
            first_name=options.get("first_name"),
            last_name=options.get("last_name"),
            role=options.get("role"),
            phone_number=options.get("phone_number"),
            backup_phone_number=options.get("backup_phone_number"),
        )
        user.set_password(options.get("password"))
        try:
            user.save()
        except IntegrityError as i:
            raise CommandError(str(i))
        except DataError as d:
            raise CommandError(str(d))

        self.stdout.write(
            self.style.SUCCESS(f'User "{user.username}" created successfully.')
        )
