from rest_framework.permissions import BasePermission

from accounts.models import Profile


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.groups.filter(name='Admin').count() > 0


class IsAccountant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.groups.filter(name='Accountant').count() > 0


class IsCoordinator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.groups.filter(name='Coordinator').count() > 0


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.groups.filter(name='Teacher').count() > 0


class IsHR(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.groups.filter(name='HR').count() > 0


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.groups.filter(name='Staff').count() > 0


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.groups.filter(name='Student').count() > 0
