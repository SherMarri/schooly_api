from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from academics import models, serializers, permissions
from common.permissions import IsAdmin, IsTeacher
from notifications.serializers import NotificationSerializer
from structure.models import Grade, Section
from notifications.views import NotificationViewSet


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
        Lists the grades in the system
        If summary flag is true, return grades with their summaries
        """
        if 'summary' in request.query_params and \
            request.user.groups.filter(name='Admin').count() > 0:
            return self.list_grades_summary()
        return super().list(self, request, args, kwargs)

    @action(detail=True, methods=['get'])
    def notifications(self, request, pk=None):
        params = request.query_params
        queryset = NotificationViewSet.get_filtered_queryset(params)
        paginator = Paginator(queryset.order_by('-created_at'), 10)
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
    permission_classes = (IsAdmin,)
    serializer_class = serializers.GradeSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        """
        Lists the sections in the system
        """
        return super().list(request, args, kwargs)

    @action(detail=True, methods=['get'])
    def notifications(self, request, pk=None):
        params = request.query_params
        queryset = NotificationViewSet.get_filtered_queryset(params)
        paginator = Paginator(queryset.order_by('-created_at'), 10)
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
        ).prefetch_related(
            'sections__students', 'sections__subjects__subject',
        ).filter(
            sections__is_active=True, sections__students__is_active=True
        )

        total_students = 0
        total_subjects = 0
        total_teachers = 0
        total_attendance = 0
        session_attendance = []

        grades = {}
        for g in grade_set:
            grade = {
                'id': g.id,
                'name': g.name,
                'students': 0,
                'sections': g.sections.count(),
                'teachers': 0,
                'attendance': 0
            }
            for section in g.sections:
                grade['students'] += section.students.count()

            # TODO


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
