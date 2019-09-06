from django.core.management.base import BaseCommand
from structure import models as structure_models
from accounts import models


class Command(BaseCommand):
    """
    Creates dummy students
    """
    help = "Creates dummy students for simulation"

    def add_arguments(self, parser):
        parser.add_argument(
            'students_per_section', type=int,
            help='Indicates the number of students per section to be created')

    def handle(self, *args, **options):
        students_per_section = options['students_per_section']
        sections = structure_models.Section.objects.all().select_related('grade')
        year = '19'
        count = 0
        for s in sections:
            students = []
            student_infos = []
            for i in range(students_per_section):
                username = get_username(year, count)
                count += 1

                s_user = models.User(username=username)
                s_user.set_password('student1234')
                students.append(s_user)

                info = models.StudentInfo(gr_number=username, section_id=s.id)
                student_infos.append(info)

            # Create users
            models.User.objects.bulk_create(students)

            # Create infos
            models.StudentInfo.objects.bulk_create(student_infos)

            # Create profiles
            students = models.User.objects.all().order_by('-id')[:students_per_section]
            student_infos = models.StudentInfo.objects.all().order_by('-id')[:students_per_section]
            profiles = []
            for student, info in zip(students, student_infos):
                profile = models.Profile(
                    user_id=student.id, profile_type=models.Profile.STUDENT,
                    student_info=info, fullname=student.username
                )
                profiles.append(profile)

            models.Profile.objects.bulk_create(profiles)

        self.stdout.write(f'Created {students_per_section} students per section.')


def get_username(year, count):
    c = str(count)
    return year + (4 - len(c)) * '0' + c
