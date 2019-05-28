from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from common.permissions import IsAdmin
from structure import models, serializers


class GradeViewSet(ListModelMixin, GenericViewSet):
    queryset = models.Grade.objects.all().prefetch_related('sections')
    permission_classes = (IsAdmin,)
    serializer_class = serializers.GradeSerializer
