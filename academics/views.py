from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from academics import models, serializers
from common import permissions


class SubjectViewSet(ModelViewSet):
    queryset = models.Subject.objects.filter(is_active=True)
    serializer_class = serializers.SubjectSerializer
    permission_classes = (permissions.IsAdmin,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
