from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from accounts import models

ADMIN = 1
STAFF = 2
TEACHER = 3
STUDENT = 4
PARENT = 5

ProfileTypes = {
    ADMIN: 'Admin',
    STAFF: 'Staff',
    TEACHER: 'Teacher',
    STUDENT: 'Student',
    PARENT: 'Parent',
}


class Command(BaseCommand):
    """
    Assigns groups to existing users according to their profile type
    Add the following profile_type users to STAFF:STAFF, TEACHER, ADMIN
    Add the following profile_type users to TEACHER:TEACHER
    Add the following profile_type users to ADMIN:ADMIN
    """
    help = "Assigns groups to existing users according to their profile type"

    def handle(self, *args, **options):
        users = models.User.objects.filter(
            is_active=True, profile__isnull=False, profile__student_info=None,
        )
        for user in users:
            if user.profile.profile_type == STAFF or user.profile.profile_type == ADMIN or user.profile.profile_type == TEACHER:
                staff_group = Group.objects.get(name='Staff')
                user.groups.add(staff_group)
            if user.profile.profile_type == TEACHER:
                teacher_group = Group.objects.get(name='Teacher')
                user.groups.add(teacher_group)
            if user.profile.profile_type == ADMIN:
                admin_group = Group.objects.get(name='Admin')
                user.groups.add(admin_group)

        self.stdout.write('Groups assigned to users.')