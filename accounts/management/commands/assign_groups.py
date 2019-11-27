from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from accounts import models

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
        staff_group = Group.objects.get(name='Staff')
        for user in users:
            if user.profile.profile_type != models.Profile.STUDENT:
                user.groups.add(staff_group)
            if user.profile.profile_type == models.Profile.TEACHER:
                teacher_group = Group.objects.get(name='Teacher')
                user.groups.add(teacher_group)
            if user.profile.profile_type == models.Profile.ADMIN:
                admin_group = Group.objects.get(name='Admin')
                user.groups.add(admin_group)

        self.stdout.write('Groups assigned to users.')
