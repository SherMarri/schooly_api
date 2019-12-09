from rest_framework import serializers
from attendance import models
from accounts.models import Profile
from accounts.serializers import StudentSerializer
from accounts.serializers import StaffSerializer
from academics.serializers import SectionSerializer

from datetime import datetime


class DailyStudentAttendanceSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField(read_only=True)
    section = SectionSerializer(read_only=True)
    section_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=models.Section.objects.filter(is_active=True),
        source='section'
    )

    class Meta:
        model = models.DailyStudentAttendance
        fields = ('id', 'section', 'section_id', 'date', 'session',
                  'created_by', 'creator', 'average_attendance',)
        read_only_fields = ('creator', 'section', 'average_attendance',)

    def get_creator(self, instance):
        if not instance.created_by:
            return None
        return {
            'id': instance.created_by.id,
            'fullname': instance.created_by.profile.fullname,
        }

    def validate_date(self, date):
        if models.DailyStudentAttendance.objects.filter(date=date, section_id=self.initial_data['section_id']).exists():
            raise serializers.ValidationError('Attendance already exists for given date.')
        return date

    def validate_created_by(self, user):
        try:
            if self.context['request'].user.id == user.id:
                return user
        except:
            raise serializers.ValidationError('Invalid user id')
        else:
            raise serializers.ValidationError('Invalid user id')

    def create(self, validated_data):
        instance = models.DailyStudentAttendance.objects.create(**validated_data)
        # Create attendance items for each student in section
        student_ids = models.User.objects.filter(
            is_active=True, profile__student_info__section_id=instance.section_id
        ).values_list('id', flat=True)
        student_ids = [id for id in student_ids]
        items = []
        for id in student_ids:
            item = models.StudentAttendanceItem(
                attendance_id=instance.id, student_id=id,
                date=validated_data['date']
            )
            items.append(item)
        models.StudentAttendanceItem.objects.bulk_create(items)
        return instance


class StudentAttendanceItemSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)

    class Meta:
        model = models.StudentAttendanceItem
        fields = ('__all__')


class DailyStudentAttendanceDetailsSerializer(serializers.ModelSerializer):
    """
    Read only serializer for representing daily student attendance and its items
    """
    creator = serializers.SerializerMethodField()
    section = SectionSerializer(read_only=True)
    items = serializers.SerializerMethodField()

    class Meta:
        model = models.DailyStudentAttendance
        fields = ('id', 'date', 'section', 'section_id', 'session',
                  'created_by', 'items', 'creator', 'average_attendance',)
        read_only_fields = ('creator', 'items', 'section', 'average_attendance',)

    def get_creator(self, instance):
        if not instance.created_by:
            return None
        return {
            'id': instance.created_by.id,
            'fullname': instance.created_by.profile.fullname,
        }

    def get_items(self, instance):
        queryset = models.StudentAttendanceItem.objects.filter(
            attendance=instance, is_active=True
        ).select_related('student__profile__student_info')
        serializer = StudentAttendanceItemSerializer(queryset, many=True)
        return serializer.data


class DailyStaffAttendanceSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.DailyStaffAttendance
        fields = ('id', 'date', 'session',
                  'created_by', 'creator', 'average_attendance',)
        read_only_fields = ('creator', 'average_attendance',)

    def get_creator(self, instance):
        if not instance.created_by:
            return None
        return {
            'id': instance.created_by.id,
            'fullname': instance.created_by.profile.fullname,
        }

    def validate_date(self, date):
        if models.DailyStaffAttendance.objects.filter(date=date).exists():
            raise serializers.ValidationError('Attendance already exists for given date.')
        return date

    def validate_created_by(self, user):
        try:
            if self.context['request'].user.id == user.id:
                return user
        except:
            raise serializers.ValidationError('Invalid user id')
        else:
            raise serializers.ValidationError('Invalid user id')

    def create(self, validated_data):
        instance = models.DailyStaffAttendance.objects.create(**validated_data)
        # Create attendance items for all staff
        staff_ids = models.User.objects.filter(
            is_active=True, profile__profile_type=Profile.STAFF
        ).values_list('id', flat=True)
        staff_ids = [id for id in staff_ids]
        items = []
        for id in staff_ids:
            item = models.StaffAttendanceItem(
                attendance_id=instance.id, employee_id=id,
                date=validated_data['date']
            )
            items.append(item)
        models.StaffAttendanceItem.objects.bulk_create(items)
        return instance


class StaffAttendanceItemSerializer(serializers.ModelSerializer):
    employee = StaffSerializer(read_only=True)

    class Meta:
        model = models.StaffAttendanceItem
        fields = ('__all__')


class DailyStaffAttendanceDetailsSerializer(serializers.ModelSerializer):
    """
    Read only serializer for representing daily student attendance and its items
    """
    creator = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    class Meta:
        model = models.DailyStaffAttendance
        fields = ('id', 'date', 'session',
                  'created_by', 'items', 'creator', 'average_attendance',)
        read_only_fields = ('creator', 'items', 'average_attendance',)

    def get_creator(self, instance):
        if not instance.created_by:
            return None
        return {
            'id': instance.created_by.id,
            'fullname': instance.created_by.profile.fullname,
        }

    def get_items(self, instance):
        queryset = models.StaffAttendanceItem.objects.filter(
            attendance=instance, is_active=True
        ).select_related('employee__profile__staff_info')
        serializer = StaffAttendanceItemSerializer(queryset, many=True)
        return serializer.data
