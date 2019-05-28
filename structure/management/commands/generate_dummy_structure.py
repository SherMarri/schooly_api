from django.core.management.base import BaseCommand, CommandError
from structure import models


class Command(BaseCommand):
    """
    Creates dummy classes and sections
    """
    help = "Creates dummy classes and sections for simulation"

    def add_arguments(self, parser):
        parser.add_argument('classes', type=int, help='Indicates the number of class to be created')
        parser.add_argument('sections', type=int, help='Indicates the number of sections per class to be created')

    def handle(self, *args, **options):
        total_classes = options['classes']
        total_sections = options['sections']

        for i in range(1, total_classes+1):
            grade = models.Grade(name=f'Class {i}')
            grade.save()
            sections = []
            for j in range(total_sections):
                sections.append(models.Section(name=f'Section {chr(j+65)}', grade_id=grade.id))
            models.Section.objects.bulk_create(sections)

        self.stdout.write(f'Created {total_classes} classes and {total_sections} sections per class')
