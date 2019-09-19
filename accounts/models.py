from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from common.models import BaseModel
from structure.models import Section

User = get_user_model()

MALE = 1
FEMALE = 2
GenderTypes = (
    (MALE, 'Male'),
    (FEMALE, 'Female'),
)

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
    fullname = models.CharField(max_length=128)
    contact = models.CharField(max_length=20, null=True, blank=True)
    student_info = models.OneToOneField('StudentInfo', null=True,
        on_delete=models.SET_NULL, related_name='profile')
    staff_info = models.OneToOneField('StaffInfo', null=True,
        on_delete=models.SET_NULL, related_name='profile')
    

    def __str__(self):
        return f'Profile for {self.user.username}'


class StudentInfo(BaseModel):
    gr_number = models.CharField(max_length=20, unique=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True,
                                blank=True, related_name='students')
    date_enrolled = models.DateField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=3, null=True, blank=True)
    address = models.TextField(max_length=128, null=True, blank=True)
    guardian_name = models.CharField(max_length=128, null=True, blank=True)
    guardian_contact = models.CharField(max_length=20, null=True, blank=True)
    gender = models.IntegerField(choices=GenderTypes, default=MALE)

    def __str__(self):
        return self.gr_number


class StaffInfo(BaseModel):
    date_hired = models.DateField(default=timezone.now())
    salary = models.FloatField(default=0)
    designation = models.CharField(max_length=128)
    address = models.TextField(max_length=128, null=True, blank=True)
