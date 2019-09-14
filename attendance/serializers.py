from rest_framework import serializers
from attendance import models
from accounts.serializers import StudentSerializer

class StudentAttendance(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=models.User.objects.all(),
        source='student'
    )

    class Meta:
        model = models.StudentAttendance
        fields = ('id', 'student_id', 'student', 'status', 'date', 'submitted_by')
