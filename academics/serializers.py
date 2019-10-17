from academics import models
from rest_framework import serializers
from structure.models import Grade, Section
from common.models import Session
from common.se

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subject
        fields = ('id', 'name')


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'name', 'grade')


class GradeSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Grade
        fields = ('id', 'name', 'sections')


class SectionSubjectSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=models.Subject.objects.filter(is_active=True),
        source='subject'
    )
    section = SectionSerializer(read_only=True)
    section_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=models.Section.objects.filter(is_active=True),
        source='section'
    )
    teacher = serializers.SerializerMethodField()
    teacher_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=models.User.objects.filter(is_active=True),
        source='teacher',
        required=False,
    )

    class Meta:
        model = models.SectionSubject
        fields = ('id', 'subject', 'subject_id', 'section', 'section_id',
            'teacher', 'teacher_id',
        )

    def get_teacher(self, instance):
        if not instance.teacher:
            return None
        return {
            'id': instance.teacher.id,
            'fullname': instance.teacher.profile.fullname,
        }


class AssessmentSerializer(serializers.ModelSerializer):

    section_subject = SectionSubjectSerializer(read_only=True)
    section_subject_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=models.SectionSubject.objects.filter(is_active=True),
        source='section_subject'
    )    

    class Meta:
        model = models.Assessment
        fields = ('id', 'name', 'section_subject', 'section_subject_id',
            'total_marks', 'date', 'session', 'graded',
        )


class StudentAssessmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.StudentAssessment
        fields = (
            'id', 'student', 'assessment', 'obtained_marks', 'comments',
        )