from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
)
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.response import Response
from functools import reduce
from attendance import serializers
from attendance import models
from common.permissions import IsAdmin
import os
import datetime
import csv
from django.conf import LazySettings
settings = LazySettings()



class DailyStudentAttendanceViewSet(
    CreateModelMixin, ListModelMixin,
    RetrieveModelMixin, GenericViewSet,
    UpdateModelMixin):
    serializer_class = serializers.DailyStudentAttendanceSerializer
    queryset = models.DailyStudentAttendance.objects.filter(is_active=True)
    permission_classes = (IsAdmin,)

    def list(self, request, *args, **kwargs):
        params = request.query_params
        queryset = self.get_filtered_queryset(**params)
        paginator = Paginator(queryset, 30)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)
        results = {}
        results['data'] = self.serializer_class(page, many=True).data
        results['page'] = page.number
        results['count'] = paginator.count
        return Response(status=status.HTTP_200_OK, data=results)

    def create(self, request, *args, **kwargs):
        data = request.data
        current_session = models.Session.objects.filter(is_active=True).first()
        if not current_session:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'message': 'No active session found',
            })
        data['session'] = current_session.id
        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        params = request.query_params
        if 'download' in params and params['download'] == 'true':
            return self.get_downloadable_link(instance)
        serializer = serializers.DailyStudentAttendanceDetailsSerializer(
            instance=instance
        )
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, *args, **kwargs):
        """
        For updating items of a daily student attendance entry
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
                matched_item.status = item['status']
                if 'comments' in item:
                    matched_item.comments = item['comments']
            items = items.values()
            if len(items) > 0:
                models.StudentAttendanceItem.objects.bulk_update(
                    items, ['status', 'comments']
                )
                instance.average_attendance = self.get_average_attendance(items)
                instance.save()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def get_average_attendance(items):
        present = reduce(
            lambda x, y: x + 1 if y.status == models.StudentAttendanceItem.PRESENT else x,
            items, 0.0
        )
        return present / len(items) * 100.0 if len(items) > 0 else 0

    @staticmethod
    def get_filtered_queryset(params):
        queryset = models.DailyStudentAttendance.objects.filter(is_active=True)
        if 'section_id' in params:
            queryset = queryset.filter(section_id=params['section_id'])
        if 'start_date' in params:
            queryset = queryset.filter(date__gte=params['start_date'])
        if 'end_date' in params:
            queryset = queryset.filter(date__lte=params['end_date'])
        return queryset.order_by('-date')

    @staticmethod
    def get_downloadable_link(instance):
        instance = models.DailyStudentAttendance.objects.filter(id=instance.id).prefetch_related(
            'items__student__profile__student_info').first()
        timestamp = datetime.datetime.now().strftime("%f")
        date = instance.date.strftime('%Y_%m_%d')
        grade = instance.section.grade
        section = instance.section.name
        file_name = f'{grade}_{section}_attendance_{date}_{timestamp}.csv'
        with open(os.path.join(settings.BASE_DIR, f'downloadables/{file_name}'), mode='w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow([
                'GR Number', 'Full Name', 'Status', 'Comments'
            ])
            for attendance_item in instance.items.all():
                writer.writerow(DailyStudentAttendanceViewSet.get_csv_row(attendance_item))
        return Response(file_name, status=status.HTTP_200_OK)

    @staticmethod
    def get_csv_row(item):
        status = None
        if item.status == models.StudentAttendanceItem.PRESENT:
            status = 'P'
        elif item.status == models.StudentAttendanceItem.ABSENT:
            status = 'A'
        elif item.status == models.StudentAttendanceItem.LEAVE:
            status = 'L'
        return [
            item.student.profile.student_info.gr_number,
            item.student.profile.fullname,
            status,
            item.comments
        ]

