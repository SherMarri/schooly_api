from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin

from attendance import serializers
from attendance import models


class StudentAttendanceViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = serializers.StudentAttendance

    def get_permissions(self):
        """
        TODO:
        If request.method === 'GET':
            return CanViewAttendance (student, staff, teacher, admin)
        Else if request.method === 'POST':
            return CanPostAttendance (staff, teacher, admin)
        """
        pass

    def get_queryset(self):
        """
        If request.user.profile.profile_type === 'Student':
            return student's attendance only
        If request.user.profile.profile_type === 'Parent':
            return their child's attendance only
        If request.user.profile.profile_type === 'Teacher':
            return queryset containing records of all sections that teacher is teaching
        If request.user.profile.profile_type === 'Staff' or 'Admin':
            return all attendance
            
        """
        pass

    def create(self, request):
        # TODO
        pass

    def list(self, request):
        # TODO
        pass