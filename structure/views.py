from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework import status


from common.permissions import IsAdmin
from structure import models, serializers


class GradeViewSet(ModelViewSet):
    queryset = models.Grade.objects.filter(is_active=True).prefetch_related('sections')
    permission_classes = (IsAdmin,)
    serializer_class = serializers.GradeSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
