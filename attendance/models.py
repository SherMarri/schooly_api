from django.db import models
from common.models import BaseModel, Session
from django.contrib.auth import get_user_model
from structure.models import Section

User = get_user_model()


class DailyStudentAttendance(BaseModel):
    section = models.ForeignKey(
        Section, on_delete=models.SET_NULL, null=True,
        related_name='student_attendances'
    )
    date = models.DateField()
    average_attendance = models.FloatField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='created_student_attendances'
    )
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name='student_attendances'
    )


class DailyStaffAttendance(BaseModel):
    date = models.DateField()
    average_attendance = models.FloatField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='created_staff_attendances'
    )
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name='staff_attendances'
    )

class StudentAttendanceItem(BaseModel):
    attendance = models.ForeignKey(
        DailyStudentAttendance, on_delete=models.SET_NULL, null=True,
        related_name='items'
    )
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
    status = models.IntegerField(choices=StatusChoices, null=True, blank=True)
    comments = models.TextField(max_length=128, null=True, blank=True)
    submitted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='submitted_student_attendances'
    )
    date = models.DateField()


class StaffAttendanceItem(BaseModel):
    attendance = models.ForeignKey(
        DailyStaffAttendance, on_delete=models.SET_NULL, null=True,
        related_name='items'
    )
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
    status = models.IntegerField(choices=StatusChoices, null=True, blank=True)
    comments = models.TextField(max_length=128, null=True, blank=True)
    submitted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='submitted_staff_attendances'
    )
    date = models.DateField()
