from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from academics import models, serializers, permissions
from common.permissions import IsAdmin, IsTeacher
from notifications.serializers import NotificationSerializer
from structure.models import Grade, Section
from accounts import models as AccountModels
from notifications.views import NotificationViewSet
from attendance.views import DailyStudentAttendanceViewSet
from rest_framework.views import APIView
from attendance.serializers import DailyStudentAttendanceSerializer
from attendance.models import StudentAttendanceItem
from accounts.serializers import StudentSerializer
from academics.services import exams
from django.conf import LazySettings
import os
import datetime
import csv

settings = LazySettings()


class GradeViewSet(ModelViewSet):
    queryset = Grade.objects.filter(is_active=True).prefetch_related('sections')
    permission_classes = (IsAdmin,)
    serializer_class = serializers.GradeSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        """
        Lists the grades in the system.
        If summary flag is true, return grades with their summaries
        """
        if 'summary' in request.query_params and \
                request.user.groups.filter(name='Admin').count() > 0:
            return self.list_grades_summary()
        return super().list(self, request, args, kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the grade with summary.
        If summary flag is true, return grades with their summaries
        """
        if 'summary' in request.query_params and \
                request.user.groups.filter(name='Admin').count() > 0:
            instance = self.get_object()
            return self.get_grade_summary(instance)
        return super().retrieve(self, request, args, kwargs)

    def list_grades_summary(self):
        """
        Method for returning following information in response:
        1. Total students
        2. Total subjects
        3. Total teachers
        4. Total attendance (current session)
        5. Month-wise attendance stats for graph
        6. Classes table with following info:
            i. Name
            ii. Strength
            iii. Subjects
            iv: Teachers
            v: Attendance
        """
        grade_set = Grade.objects.filter(
            is_active=True
        )

        grades = {}
        for grade_info in grade_set:
            grade = {
                'id': grade_info.id,
                'name': grade_info.name,
                'students': AccountModels.StudentInfo.objects.filter(is_active=True,
                                                                     section__grade_id=grade_info.id).count(),
                'subjects': models.SectionSubject.objects.filter(
                    section__grade_id=grade_info.id, is_active=True).distinct('subject_id').count(),
                'sections': models.Section.objects.filter(grade_id=grade_info.id).count(),
                'teachers': models.SectionSubject.objects.filter(
                    section__grade_id=grade_info.id, is_active=True).distinct('teacher_id').count(),
                'attendance': 0
            }
            grades[grade_info.id] = grade

        result = {
            'items': grades.values(),
            'students': AccountModels.StudentInfo.objects.filter(is_active=True).count(),
            'teachers': AccountModels.StaffInfo.objects.filter(is_active=True).count(),
            'subjects': models.Subject.objects.filter(is_active=True).count(),
            'attendance': 79,
            'monthly_attendance': [
                {
                    'month': 'January',
                    'value': 76
                }
            ]
        }

        return Response(status=status.HTTP_200_OK, data=result)

        # TODO

    def get_grade_summary(self, instance):

        sections = {}
        for section_info in instance.sections.all():
            section = {
                'id': section_info.id,
                'name': section_info.name,
                'students': AccountModels.StudentInfo.objects.filter(is_active=True,
                                                                     section_id=section_info.id).count(),
                'subjects': models.SectionSubject.objects.filter(
                    section_id=section_info.id, is_active=True).distinct('subject_id').count(),
                'attendance': 80,
            }
            sections[section_info.id] = section
        result = {
            'name': instance.name,
            'students': AccountModels.StudentInfo.objects.filter(is_active=True, section__grade_id=instance.id).count(),
            'subjects': models.SectionSubject.objects.filter(
                section__grade_id=instance.id, is_active=True).distinct('subject_id').count(),
            'sections': sections.values(),
            'teachers': models.SectionSubject.objects.filter(
                section__grade_id=instance.id, is_active=True).distinct('teacher_id').count(),
            'attendance': 79,
            'monthly_attendance': [
                {
                    'month': 'January',
                    'value': 76
                }
            ]
        }

        return Response(status=status.HTTP_200_OK, data=result)

        # TODO

    @action(detail=True, methods=['get'])
    def notifications(self, request, pk=None):
        params = request.query_params
        queryset = NotificationViewSet.get_filtered_queryset(params)
        paginator = Paginator(queryset.order_by('-created_at'), 10)
        if 'recent' in params:
            paginator = Paginator(queryset.order_by('-created_at'), 5)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)
        serializer = NotificationSerializer(page, many=True)
        results = {}
        results['data'] = serializer.data
        results['page'] = page.number
        results['count'] = paginator.count
        return Response(status=status.HTTP_200_OK, data=results)


class SectionViewSet(ModelViewSet):
    queryset = Section.objects.filter(is_active=True)
    # permission_classes = (IsAdmin, IsTeacher)
    serializer_class = serializers.SectionSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        """
        Lists the sections in the system
        """
        if 'role' in request.query_params and request.query_params['role'] == 'teacher':
            return self.list_teacher_sections()
        return super().list(request, args, kwargs)

    def list_teacher_sections(self):
        queryset = models.Section.objects.filter(
            is_active=True, subjects__teacher_id=self.request.user.id
        ).select_related('grade')
        serializer = serializers.SectionSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the section.
        If summary flag is true, return section with their summaries
        """
        if 'summary' in request.query_params and \
                request.user.groups.filter(name='Admin').count() > 0:
            instance = self.get_object()
            return self.get_section_summary(instance)
        return super().retrieve(self, request, args, kwargs)

    @action(detail=True, methods=['get'])
    def notifications(self, request, pk=None):
        params = request.query_params
        queryset = NotificationViewSet.get_filtered_queryset(params)
        paginator = Paginator(queryset.order_by('-created_at'), 10)
        if 'recent' in params:
            paginator = Paginator(queryset.order_by('-created_at'), 5)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)
        serializer = NotificationSerializer(page, many=True)
        results = {}
        results['data'] = serializer.data
        results['page'] = page.number
        results['count'] = paginator.count
        return Response(status=status.HTTP_200_OK, data=results)

    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        instance = self.get_object()
        params = request.query_params
        queryset = DailyStudentAttendanceViewSet.get_filtered_queryset(
            params
        )
        if 'download' in params:
            queryset = queryset.prefetch_related(
                'items__student__profile__student_info'
            ).order_by('date')
            return self.handle_download_attendance(queryset)
        paginator = Paginator(queryset, 30)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)
        serializer = DailyStudentAttendanceSerializer(page, many=True)
        results = {}
        results['data'] = serializer.data
        results['page'] = page.number
        results['count'] = paginator.count
        return Response(status=status.HTTP_200_OK, data=results)

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        instance = self.get_object()
        params = request.query_params
        queryset = models.User.objects.filter(
            profile__student_info__section_id=instance.id, is_active=True
        ).select_related('profile__student_info')
        if 'download' in params and params['download'] == 'true':
            return self.get_downloadable_link(queryset)
        serializer = StudentSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=True, methods=['get', 'post', 'put'])
    def subjects(self, request, pk=None):
        if request.method == 'POST':
            return self.add_subject()
        elif request.method == 'PUT':
            return self.update_subject_assignment()
        else:
            return self.get_subjects()

    def get_subjects(self):
        instance = self.get_object()
        if 'role' in self.request.query_params and self.request.query_params['role'] == 'teacher':
            queryset = models.SectionSubject.objects.filter(
                section_id=instance.id, teacher_id=self.request.user.id, is_active=True,
            )
        else:
            queryset = models.SectionSubject.objects.filter(
                section_id=instance.id, is_active=True,
            )
        serializer = serializers.SectionSubjectSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def add_subject(self):
        data = self.request.data
        serializer = serializers.SectionSubjectSerializer(data=data)
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(status=status.HTTP_200_OK, data=serializer.data)
        except ValidationError as exception:
            errors = serializer.errors
            if 'non_field_errors' in errors:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={
                    'code': 'SUBJECT_EXISTS',
                    'message': 'This subject already exists in this section.'
                })
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    def update_subject_assignment(self):
        data = self.request.data
        if 'id' not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'message': 'No section subject id provided'
            })
        section_subject = models.SectionSubject.objects.filter(id=data['id']).first()

        if not section_subject:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'message': 'No section subject found with given id'
            })
        instance = self.get_object()
        serializer = serializers.SectionSubjectSerializer(
            instance=section_subject, data=data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            section = serializer.validated_data['section']
            if section.id != instance.id:
                return Response(
                    status=status.HTTP_200_OK,
                    data={
                        'message': 'Cannot assign subject to another section using current API Endpoint'
                    }
                )
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=True, methods=['get', 'post', 'put'])
    def assessments(self, request, pk=None):
        """
        Handles following operations:
        1. GET: Return paginated assessments
        2. POST: Create assessment for section
        3. PUT: Update student marks/points in assessment
        """
        if request.method == 'POST':
            try:
                assessment = AssessmentViewSet.add_assessment(request.data)
                return Response(status=status.HTTP_200_OK, data=assessment)
            except ValidationError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=e.errors)

        elif request.method == 'PUT':
            return AssessmentViewSet.update_assessment(request.data)
        else:
            instance = self.get_object()
            data = AssessmentViewSet.get_assessments(request.query_params, instance.id)
            return Response(status=status.HTTP_200_OK, data=data)

    @staticmethod
    def get_downloadable_link(queryset):
        timestamp = datetime.datetime.now().strftime("%f")
        file_name = f'section_students_{timestamp}.csv'
        with open(os.path.join(settings.BASE_DIR, f'downloadables/{file_name}'), mode='w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow([
                'GR Number', 'Full Name', 'Average Attendance'
            ])
            for student in queryset:
                writer.writerow(SectionViewSet.get_csv_row(student))
        return Response(file_name, status=status.HTTP_200_OK)

    @staticmethod
    def get_csv_row(student):
        return [
            student.profile.student_info.gr_number, student.profile.fullname, '75%'
        ]

    @staticmethod
    def handle_download_attendance(queryset):
        timestamp = datetime.datetime.now().strftime("%f")
        dates = []
        students = {}
        date_format = '%d/%m/%Y'
        for attendance in queryset:
            formatted_date = attendance.date.strftime(date_format)
            dates.append(formatted_date)
            for item in attendance.items.all():
                student_name = f'{item.student.profile.fullname} ({item.student.profile.student_info.gr_number})'
                if student_name not in students:
                    students[student_name] = {}
                    students[student_name]['total_presents'] = 0
                attendance_status = ''
                if item.status == StudentAttendanceItem.PRESENT:
                    attendance_status = 'P'
                    students[student_name]['total_presents'] = students[student_name]['total_presents'] + 1
                elif item.status == StudentAttendanceItem.ABSENT:
                    attendance_status = 'A'
                elif item.status == StudentAttendanceItem.LEAVE:
                    attendance_status = 'L'
                students[student_name][formatted_date] = attendance_status

        file_name = f'attendance_{timestamp}.csv'
        with open(os.path.join(settings.BASE_DIR, f'downloadables/{file_name}'), mode='w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(['Student'] + ['Average %'] + dates)
            for key, statuses in students.items():
                writer.writerow(SectionViewSet.get_attendance_row(key, statuses, dates))
        return Response(status=status.HTTP_200_OK, data=file_name)

    @staticmethod
    def get_attendance_row(student, values, dates):
        average_attendance = round(values['total_presents']/len(dates) * 100, 1)
        return [student] + [average_attendance] + [values[date] if date in values else '' for date in dates]

    def get_section_summary(self, instance):
        result = {
            'section_name': instance.name,
            'grade_name': instance.grade.name,
            'students': AccountModels.StudentInfo.objects.filter(is_active=True, section_id=instance.id).count(),
            'subjects': models.SectionSubject.objects.filter(
                section_id=instance.id, is_active=True).distinct('subject_id').count(),
            'teachers': models.SectionSubject.objects.filter(
                section_id=instance.id, is_active=True).distinct('teacher_id').count(),
            'attendance': 79,
            'monthly_attendance': [
                {
                    'month': 'January',
                    'value': 76
                }
            ]
        }

        return Response(status=status.HTTP_200_OK, data=result)

        # TODO


class AssessmentViewSet(ModelViewSet):
    serializer_class = serializers.AssessmentSerializer
    queryset = models.Assessment.objects.filter(is_active=True)
    permission_classes = (IsAdmin,)

    def list(self, request, *args, **kwargs):
        pass

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        params = request.query_params
        if 'download' in params and params['download'] == 'true':
            return self.get_downloadable_link(instance)
        serializer = serializers.AssessmentDetailsSerializer(
            instance=instance
        )
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, *args, **kwargs):
        """
        For updating items of a student assessment entry
        """
        data = request.data
        instance = self.get_object()
        if 'items' in data:
            items = instance.items.all()
            items = {i.id: i for i in items}
            for item in data['items']:
                matched_item = items.get(item['id'], None)
                if matched_item is None:
                    continue
                matched_item.obtained_marks = item['obtained_marks']
                if 'comments' in item:
                    matched_item.comments = item['comments']
            items = items.values()
            if len(items) > 0:
                models.StudentAssessment.objects.bulk_update(
                    items, ['obtained_marks', 'comments']
                )
                instance.save()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def get_assessments(params, section_id):
        queryset = AssessmentViewSet.get_filtered_queryset(params, section_id)
        paginator = Paginator(queryset, 20)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)
        serializer = serializers.AssessmentSerializer(page, many=True)
        results = {}
        results['data'] = serializer.data
        results['page'] = page.number
        results['count'] = paginator.count
        return results

    @staticmethod
    def add_assessment(data):
        data = data.copy()
        data['session_id'] = models.Session.objects.filter(is_active=True).first().id
        serializer = serializers.AssessmentSerializer(data=data)
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return serializer.data
        except ValidationError as e:
            raise e

    @staticmethod
    def update_assessment(data):
        pass

    @staticmethod
    def get_filtered_queryset(params, section_id):
        queryset = models.Assessment.objects.filter(
            is_active=True, section_subject__section_id=section_id, exam=None,
        )
        if 'section_subject_id' in params and params['section_subject_id'] != '-1':
            queryset = queryset.filter(section_subject_id=params['section_subject_id'])
        # if 'graded' in params and params['graded'] != '-1':
        #     graded_value = True if params['graded'] == 'true' else False
        #     queryset = queryset.filter(graded=graded_value)
        if 'start_date' in params:
            queryset = queryset.filter(date__gte=params['start_date'])
        if 'end_date' in params:
            queryset = queryset.filter(date__lte=params['end_date'])
        return queryset.order_by('-date')

    @staticmethod
    def get_downloadable_link(instance):
        instance = models.Assessment.objects.filter(id=instance.id).prefetch_related(
            'items__student__profile__student_info').first()
        date = instance.date.strftime('%Y_%m_%d')
        grade = instance.section_subject.section.grade
        section = instance.section_subject.section.name
        name = instance.name.replace(" ", "_")
        file_name = f'{grade}_{section}_{name}_{date}.csv'
        with open(os.path.join(settings.BASE_DIR, f'downloadables/{file_name}'), mode='w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow([
                'GR Number', 'Full Name', 'Obtained Marks', 'Comments'
            ])
            for assessment_item in instance.items.all():
                writer.writerow(AssessmentViewSet.get_csv_row(assessment_item))
        return Response(file_name, status=status.HTTP_200_OK)

    @staticmethod
    def get_csv_row(item):
        return [
            item.student.profile.student_info.gr_number, item.student.profile.fullname,
            item.obtained_marks, item.comments,
        ]


class SubjectViewSet(ModelViewSet):
    queryset = models.Subject.objects.filter(is_active=True)
    serializer_class = serializers.SubjectSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAdmin | IsTeacher]
        else:
            permission_classes = [IsAdmin]
        return [permission_class() for permission_class in permission_classes]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExamsAPIView(APIView):
    # permission_classes = [IsAdmin, IsTeacher]

    def post(self, request):
        data = request.data
        try:
            if "consolidated" in data:
                exams.ExamService.create_consolidated_exam(data['name'], data['section'], data['exam_ids'])
            else:
                exams.ExamService.create_exam(data['name'], data['date'], data['section'], data['section_subjects'])
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_201_CREATED)

    def get(self, request):
        params = request.query_params
        queryset = models.Exam.objects.filter(is_active=True, section_id=params['section_id'])
        if 'section_subject_id' in params:
            queryset = queryset.filter(assessments__section_subject_id=params['section_subject_id'])
        paginator = Paginator(queryset.order_by('-created_at'), 20)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)
        serializer = serializers.ExamSerializer(page, many=True)
        results = {}
        results['data'] = serializer.data
        results['page'] = page.number
        results['count'] = paginator.count
        return Response(status=status.HTTP_200_OK, data=results)
