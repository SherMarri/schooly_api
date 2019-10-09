from rest_framework import serializers
from attendance import models
from accounts.serializers import StudentSerializer
from academics.serializers import SectionSerializer

class DailyStudentAttendanceSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField(read_only=True)
    section = SectionSerializer(read_only=True)
    section_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=models.Section.objects.filter(is_active=True),
        source='section'
    )
    class Meta:
        model = models.DailyStudentAttendance
        fields = ('id', 'date', 'section', 'section_id', 'created_by',
                  'target_type', 'target_id')
        read_only_fields = ('creator', 'section')

    def get_creator(self, instance):
        if not instance.created_by:
            return None
        return {
            'id': instance.created_by.id,
            'fullname': instance.created_by.profile.fullname,
        }

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
