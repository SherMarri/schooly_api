from django.db.models import Q
from rest_framework.permissions import BasePermission

from accounts.models import Profile


class ViewSubjectsPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated


class ChangeSubjectsPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        # return user.groups.filter(Q(name='Admin') | Q(name='Teacher')).count() > 0
        return user.groups.filter(Q(name='Admin')).count() > 0
