from django.contrib.auth import get_user_model
from django.db import models
from common.models import BaseModel

User = get_user_model()


class Notification(BaseModel):
    ORGANIZATION = 1
    CLASS = 2
    SECTION = 3
    STUDENT = 4
    TEACHER = 5
    PARENT = 6

    TargetTypes = (
        (ORGANIZATION, 'Organization'),
        (CLASS, 'Class'),
        (SECTION, 'Section'),
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (PARENT, 'Parent'),
    )

    title = models.CharField(max_length=50)
    content = models.TextField(max_length=1000)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    target_type = models.IntegerField(choices=TargetTypes, default=ORGANIZATION)
    target_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title
