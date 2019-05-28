from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from common.models import BaseModel
from structure.models import Section

User = get_user_model()


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    ADMIN = 1
    STAFF = 2
    TEACHER = 3
    STUDENT = 4
    PARENT = 5

    ProfileTypes = (
        (ADMIN, 'Admin'),
        (STAFF, 'Staff'),
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
        (PARENT, 'Parent')
    )

    profile_type = models.IntegerField(choices=ProfileTypes)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    info = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'Profile for {self.user.username}'


class Info(BaseModel):
    fullname = models.CharField(max_length=128)
    contact = models.CharField(max_length=20, null=True, blank=True)
    profile = GenericRelation(Profile)

    class Meta:
        abstract = True


class StudentInfo(Info):
    roll_number = models.CharField(max_length=20)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True,
                                blank=True, related_name='students')
    date_enrolled = models.DateField(auto_now_add=True)


class TeacherInfo(Info):
    date_hired = models.DateField(auto_now_add=True)
    salary = models.FloatField(default=0)


class StaffInfo(Info):
    date_hired = models.DateField(auto_now_add=True)
    salary = models.FloatField(default=0)
    designation = models.CharField(max_length=128)


class AdminInfo(Info):
    date_hired = models.DateField(auto_now_add=True)
    salary = models.FloatField(default=0)
