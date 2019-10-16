from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
)
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.response import Response

from attendance import serializers
from attendance import models
from common.permissions import IsAdmin

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
            models.StudentAttendanceItem.objects.bulk_update(
                items, ['status', 'comments']
            )
            instance.average_attendance = self.get_average_attendance(items)
            instance.save()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def get_average_attendance(items):
        total = 0.0
        present = 0.0
        for item in items:
            if item.status is None:
                continue
            total += 1
            if item.status == models.StudentAttendanceItem.PRESENT:
                present += 1
        return present/total * 100.0 if present > 0 else None

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
