from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from common.permissions import IsAdmin
from notifications import serializers
from notifications import models


class NotificationViewSet(ModelViewSet):
    queryset = models.Notification.objects.filter(is_active=True)
    # permission_classes = (IsAdmin,)
    serializer_class = serializers.NotificationSerializer

    def list(self, request, *args, **kwargs):
        params = request.query_params
        queryset = self.get_filtered_queryset(params)
        paginator = Paginator(queryset, 10)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)
        serializer = serializers.NotificationSerializer(page, many=True)
        results = {}
        results['data'] = serializer.data
        results['page'] = page.number
        results['count'] = paginator.count
        return Response(status=status.HTTP_200_OK, data=results)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['created_by'] = request.user.id
        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def get_filtered_queryset(params):
        queryset = models.Notification.objects.filter(is_active=True).order_by('-created_at')
        if 'target_type' in params and params['target_type'] != '-1':
            queryset = queryset.filter(target_type=params['target_type'])
        else:
            queryset = queryset.filter(target_type__in=[models.Notification.ORGANIZATION, models.Notification.STAFF, models.Notification.TEACHER])

        if 'target_id' in params:
            queryset = queryset.filter(target_id=params['target_id'])
        if 'search_term' in params:
            queryset = queryset.filter(
                Q(title__icontains=params['search_term']) | Q(content__icontains=params['search_term']))
        if 'start_date' in params:
            queryset = queryset.filter(created_at__gte=params['start_date'])
        if 'end_date' in params:
            end_date = "%s %s" % (params['end_date'], '23:59:59.000')
            queryset = queryset.filter(created_at__lte=end_date)
        return queryset
