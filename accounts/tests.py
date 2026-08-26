from django.contrib.auth import get_user_model
from django.core.management import call_command, CommandError
from django.test import TestCase

from accounts.enums import UserRole
from accounts.models import User

AUTH_USER = get_user_model()


class CreateUserCommandTest(TestCase):
    def test_create_teacher(self):
        call_command(
            "create_user",
            role="teacher",
            username="teachertest1",
            first_name="teacher",
            last_name="testi",
            phone_number="09123456789",
            backup_phone_number="09123456789",
            password="123",
        )

        user = AUTH_USER.objects.get(username="teachertest1")

        self.assertEqual(user.first_name, "teacher")
        self.assertEqual(user.last_name, "testi")
        self.assertEqual(user.role, UserRole.TEACHER)
        self.assertEqual(user.phone_number, "09123456789")
        self.assertEqual(user.backup_phone_number, "09123456789")
        self.assertTrue(user.check_password("123"))

    def test_create_teacher_without_backup_phone_number_error(self):
        with self.assertRaises(CommandError) as cm:
            call_command(
                "create_user",
                role="teacher",
                username="teachertest1",
                first_name="teacher",
                last_name="testi",
                phone_number="09123456789",
                password="123",
            )
        self.assertEqual(
            str(cm.exception),
            "backup-phone-number is required for teachers!(--bpn)",
        )
        self.assertFalse(AUTH_USER.objects.filter(username="teachertest1").exists())
