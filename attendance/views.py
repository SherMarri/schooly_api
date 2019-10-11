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
        paginator = Paginator(queryset, 20)
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
        return self.retrieve(request, *args, **kwargs)

    @staticmethod
    def get_filtered_queryset(**kwargs):
        queryset = models.DailyStudentAttendance.objects.filter(is_active=True)
        if 'section_id' in kwargs:
            queryset = queryset.filter(section_id=kwargs['section_id'])
        return queryset
