from django.db import models

from accounts.models import User
from common.models import BaseModel, Session
from structure.models import Section


class Subject(BaseModel):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class SectionSubject(BaseModel):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE,
                                related_name='sections')
    section = models.ForeignKey(Section, on_delete=models.CASCADE,
                                related_name='subjects')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='subjects')

    class Meta:
        unique_together = ['subject', 'section',]

    def __str__(self):
        return '{0} (Section {1} - Class {2}'.format(
            self.subject.name, self.section.name, self.section.grade.name)


class Assessment(BaseModel):
    name = models.CharField(max_length=128)
    section_subject = models.ForeignKey(SectionSubject, on_delete=models.CASCADE)
    total_marks = models.FloatField()
    date = models.DateField()
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)


class StudentAssessment(BaseModel):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    obtained_marks = models.FloatField(null=True, blank=True)
    comments = models.TextField(max_length=128, null=True, blank=True)
