from rest_framework.viewsets import ModelViewSet
from academics import models, serializers
from common import permissions


class SubjectViewSet(ModelViewSet):
    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer
    permission_classes = (permissions.IsAdmin,)

