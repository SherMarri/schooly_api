from rest_framework.permissions import BasePermission

from accounts.models import Profile


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               request.user.profile.profile_type == Profile.ADMIN
