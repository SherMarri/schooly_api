from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from academics import models, serializers, permissions
from common.permissions import IsAdmin, IsTeacher
from structure.models import Grade


class GradeViewSet(ModelViewSet):
    queryset = Grade.objects.filter(is_active=True).prefetch_related('sections')
    permission_classes = (IsAdmin,)
    serializer_class = serializers.GradeSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        """
        Lists the grades in the system
        If summary flag is true, return grades with their summaries
        """
        params = request.query_params


class SubjectViewSet(ModelViewSet):
    queryset = models.Subject.objects.filter(is_active=True)
    serializer_class = serializers.SubjectSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAdmin | IsTeacher]
        else:
            permission_classes = [IsAdmin]
        return [permission_class() for permission_class in permission_classes]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GradeViewSet(ModelViewSet):
    queryset = Grade.objects.filter(is_active=True).prefetch_related('sections')
    permission_classes = (IsAdmin,)
    serializer_class = serializers.GradeSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
