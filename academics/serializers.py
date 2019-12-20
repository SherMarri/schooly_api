from academics import models
from rest_framework import serializers
from structure.models import Grade, Section
from accounts.models import Profile
from accounts.serializers import StudentSerializer


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subject
        fields = ('id', 'name')


class SectionSerializer(serializers.ModelSerializer):
    grade = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ('id', 'name', 'grade')

    def get_grade(self, instance):
        return instance.grade.name


class GradeSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Grade
        fields = ('id', 'name', 'sections', 'is_active')


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


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Exam
        fields = ('id', 'name', 'date', 'consolidated', 'section_id')


class AssessmentSerializer(serializers.ModelSerializer):
    exam = ExamSerializer(read_only=True)
    section_subject = SectionSubjectSerializer(read_only=True)
    section_subject_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=models.SectionSubject.objects.filter(is_active=True),
        source='section_subject'
    )

    class Meta:
        model = models.Assessment
        fields = ('id', 'name', 'section_subject', 'section_subject_id',
                  'total_marks', 'date', 'session', 'exam',
                  )

    def create(self, validated_data):
        assessment = super().create(validated_data)
        students = models.User.objects.filter(is_active=True,
                                              profile__student_info__section_id=assessment.section_subject.section_id).values_list(
            'id', flat=True)
        student_ids = [id for id in students]
        items = []
        for id in student_ids:
            item = models.StudentAssessment(student_id=id, assessment_id=assessment.id)
            items.append(item)
        models.StudentAssessment.objects.bulk_create(items)
        return assessment


class AssessmentDetailsSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    section_subject = SectionSubjectSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)

    class Meta:
        model = models.Assessment
        fields = ('id', 'name', 'total_marks', 'date', 'exam', 'section_subject', 'items')

    def get_items(self, instance):
        queryset = models.StudentAssessment.objects.filter(
            assessment=instance, is_active=True
        ).select_related('student__profile__student_info')
        serializer = StudentAssessmentSerializer(queryset, many=True)
        return serializer.data


class StudentAssessmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)

    class Meta:
        model = models.StudentAssessment
        fields = ('id', 'student', 'student_id', 'assessment', 'obtained_marks',
                  'comments',)


class StudentAssessmentDetailsSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    assessment = AssessmentSerializer(read_only=True)

    class Meta:
        model = models.StudentAssessment
        fields = ('id', 'student', 'student_id', 'assessment', 'obtained_marks',
                  'comments',)
