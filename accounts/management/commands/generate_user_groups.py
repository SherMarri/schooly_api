from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    """
    "Creates user groups Admin, Teacher, Staff"
    """
    help = "Creates user groups Admin, Teacher, Staff"

    def handle(self, *args, **options):
        group_names = ['Admin', 'Staff', 'Teacher']
        for group in group_names:
            Group.objects.update_or_create(name=group)
        self.stdout.write('Groups created.')
