from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.response import Response

from attendance import serializers
from attendance import models
from common.permissions import IsAdmin

class DailyStudentAttendanceViewSet(
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet
    ):

    serializer_class = serializers.DailyStudentAttendanceSerializer
    queryset = models.DailyStaffAttendance.objects.filter(is_active=True)
    permission_classes = (IsAdmin,)

    def list(self, request, *args, **kwargs):
        params = request.query_params
        queryset = self.get_filtered_queryset(params)
        paginator = Paginator(queryset, 20)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)
        results = {}
        results['data'] = self.get_serializer_class(page, many=True)
        results['page'] = page.number
        results['count'] = paginator.count
        return Response(status=status.HTTP_200_OK, data=results)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer_class(
            data=data, context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)

    @staticmethod
    def get_filtered_queryset(params):
        queryset = models.DailyStaffAttendance.objects.filter(is_active=True)
        return queryset
