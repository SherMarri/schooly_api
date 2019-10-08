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
