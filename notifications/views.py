from django.core.paginator import Paginator
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
    permission_classes = (IsAdmin,)
    serializer_class = serializers.NotificationSerializer

    def list(self, request, *args, **kwargs):
        params = request.query_params
        queryset = self.get_filtered_queryset(params)
        paginator = Paginator(queryset, 20)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)
        results = {}
        results['data'] = serializers.NotificationSerializer(page, many=True)
        results['page'] = page.number
        results['count'] = paginator.count
        return Response(status=status.HTTP_200_OK, data=results)

    def create(self, request, *args, **kwargs):
        data = request.data
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
        queryset = models.Notification.objects.filter(is_active=True)
        if 'target_type' in params:
            queryset = queryset.filter(target_type=1)
        if 'target_id' in params:
            queryset = queryset.filter(target_id=1)
        return queryset

