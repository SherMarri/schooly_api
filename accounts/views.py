from django.db.models import Q
from rest_auth.views import LoginView
from django.conf import LazySettings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts import models, serializers
from common.permissions import IsAdmin

settings = LazySettings()


class CustomLoginView(LoginView):
    def get_response(self):
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': self.user,
                'token': self.token,
            }
            serializer = serializer_class(instance=data,
                                          context={'request': self.request})
        else:
            serializer = serializer_class(instance=self.token,
                                          context={'request': self.request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentsAutocompleteAPIView(APIView):
    """
    APIView for returning list of students matching query
    """
    permission_classes = (IsAdmin,)

    def get(self, request):
        q = request.GET.get('q', None)
        if q is None:  # Send empty list
            return Response(status=status.HTTP_200_OK, data=[])

        queryset = models.Profile.objects.filter(
            Q(student_info__roll_number__icontains=q) | Q(fullname__icontains=q),
            is_active=True
        ).prefetch_related('profile')[:20]

        serializer = serializers.StudentProfileSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
