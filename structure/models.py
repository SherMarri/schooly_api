from django.db import models

from common.models import BaseModel


class Grade(BaseModel):
    name = models.CharField(max_length=20,)

    def __str__(self):
        return self.name


class Section(BaseModel):
    name = models.CharField(max_length=20)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE,
                              related_name='sections')

    class Meta:
        unique_together = ['name', 'grade']

    def __str__(self):
        return '{0} (Class {1})'.format(self.name, self.grade.name)
