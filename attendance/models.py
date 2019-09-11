from django.db import models
from common.models import BaseModel
from django.contrib.auth import get_user_model


User = get_user_model()


class StudentAttendance(BaseModel):
    
    PRESENT = 1
    ABSENT = 2
    LEAVE = 3

    StatusChoices = (
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (LEAVE, 'Leave'),
    )

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='student_attendances'
    )
    status = models.IntegerField(choices=StatusChoices)
    comments = models.TextField(max_length=128)
    submitted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='submitted_student_attendances'
    )
    date = models.DateField()


class StaffAttendance(BaseModel):
    
    PRESENT = 1
    ABSENT = 2
    LEAVE = 3

    StatusChoices = (
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (LEAVE, 'Leave'),
    )

    employee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='staff_attendances'
    )
    status = models.IntegerField(choices=StatusChoices)
    comments = models.TextField(max_length=128)
    submitted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='submitted_staff_attendances'
    )
    date = models.DateField()
