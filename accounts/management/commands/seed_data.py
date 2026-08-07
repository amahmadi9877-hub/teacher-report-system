from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import DataError, IntegrityError

from accounts.enums import UserRole
from accounts.models.user import User
from core.utils import required_input, get_password

AUTH_USER = get_user_model()


class Command(BaseCommand):
    help = f"""create new sample data for new project
   """

    def add_arguments(self, parser):
        parser.add_argument("sample_number", type=int)

    def handle(self, *args, **options):
        teacher_sample = AUTH_USER(
            username=f"teacher_sample{options['sample_number']}",
            first_name="teacher",
            last_name=f"{options['sample_number']}",
            role="teacher",
            phone_number="09000000000",
            backup_phone_number="09000000000",
        )
        teacher_sample.set_password("123")

        education_officer_sample = AUTH_USER(
            username=f"education_sample{options['sample_number']}",
            first_name="education_officer",
            last_name=f"{options['sample_number']}",
            role="education_officer",
            phone_number="09000000001",
            backup_phone_number="09000000001",
        )
        education_officer_sample.set_password("123")
        finance_officer_sample = AUTH_USER(
            username=f"finance_sample{options['sample_number']}",
            first_name="finance_officer",
            last_name=f"{options['sample_number']}",
            role="finance_officer",
            phone_number="09000000001",
            backup_phone_number="09000000011",
        )
        finance_officer_sample.set_password("123")
        try:
            teacher_sample.save()
            education_officer_sample.save()
            finance_officer_sample.save()
        except IntegrityError as i:
            raise CommandError(str(i))
        except DataError as d:
            raise CommandError(str(d))

        self.stdout.write(
            self.style.SUCCESS(
                f"user1: ({teacher_sample.username},123)\nuser2: ({education_officer_sample.username},123)\nuser1: ({finance_officer_sample.username},123)\n"
            )
        )
