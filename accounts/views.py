import csv
from django.db.models import Q
from rest_auth.views import LoginView
from django.conf import LazySettings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Group

from accounts import models, serializers
from common.permissions import IsAdmin, IsHR, IsAccountant
from django.core.paginator import Paginator
from django.http import HttpResponse
import os
import datetime
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
        return Response(data=serializer.data, status=status.HTTP_200_OK)


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
            Q(student_info__gr_number__icontains=q) | Q(fullname__icontains=q),
            student_info_id__isnull=False, is_active=True
        ).select_related('student_info')[:20]

        serializer = serializers.StudentProfileSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class StudentAPIView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        data = request.data
        context = {
            'update': True if 'update' in data and data['update'] else False
        }
        serializer = serializers.CreateUpdateStudentSerializer(data=data, context=context)
        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data=serializer.errors
            )
        else:
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

    def get(self, request):
        params = request.query_params
        queryset = self.get_filtered_queryset(params)
        if 'download' in params and params['download'] == 'true':
            return self.get_downloadable_link(queryset)

        results = {}
        paginator = Paginator(queryset, 20)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)

        serializer = serializers.StudentDetailsSerializer(page, many=True)
        results['data'] = serializer.data
        results['page'] = page.number
        results['count'] = paginator.count
        return Response(status=status.HTTP_200_OK, data=results)

    def delete(self, request):
        """
        Deactivates a student account
        1. Deactivate user
        2. Deactivate profile
        3. Deactivate student info
        """
        params = request.query_params
        id = params.get('id', None)
        if id is None:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data='ID is required.'
            )
        try:
            user = models.User.objects.get(id=id)
        except:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data='Invalid ID.'
            )

        user.is_active = False
        user.save()

        profile = user.profile
        profile.is_active = False
        profile.save()

        info = profile.student_info
        info.is_active = False
        info.save()

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def get_downloadable_link(queryset):
        timestamp = datetime.datetime.now().strftime("%f")
        file_name = f'students_{timestamp}.csv'
        with open(os.path.join(settings.BASE_DIR, f'downloadables/{file_name}'), mode='w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow([
                'Roll #', 'Name', 'Section', 'Guardian',
                'Contact', 'Gender', 'Date of Birth', 'Date Enrolled', 'Address',
            ])
            for profile in queryset:
                writer.writerow(StudentAPIView.get_csv_row(profile))
        return Response(file_name, status=status.HTTP_200_OK)

    @staticmethod
    def get_csv_row(profile):
        return [
            profile.student_info.gr_number, profile.fullname,
            f'Class {profile.student_info.section.grade.name} - {profile.student_info.section.name}',
            profile.student_info.guardian_name,
            profile.student_info.guardian_contact,
            profile.student_info.get_gender_display(),
            profile.student_info.date_of_birth,
            profile.student_info.date_enrolled,
            profile.student_info.address,
        ]

    @staticmethod
    def get_filtered_queryset(params):
        filter_serializer = serializers.StudentFilterSerializer(data=params)
        if not filter_serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=filter_serializer.errors
            )

        queryset = models.Profile.objects.filter(
            is_active=True, student_info_id__isnull=False,
        )

        if 'grade_id' in params and params['grade_id'] != '-1':
            if 'section_id' in params and params['section_id'] != '-1':
                queryset = queryset.filter(
                    student_info__section_id=params['section_id']
                )
            else:
                queryset = queryset.filter(
                    student_info__section__grade_id=params['grade_id']
                )

        if 'search_term' in params and len(params['search_term']) > 0:
            q = params['search_term']
            queryset = queryset.filter(
                Q(student_info__gr_number__icontains=q) | Q(fullname__icontains=q),
            )

        queryset = queryset.select_related('student_info__section__grade')
        return queryset


class StaffAPIView(APIView):

    def get_permissions(self):
        if self.request.method in ['GET']:
            permission_classes = [IsAdmin | IsHR | IsAccountant]
        else:
            permission_classes = [IsAdmin]
        return [permission_class() for permission_class in permission_classes]

    def post(self, request):
        data = request.data
        context = {
            'update': True if 'update' in data and data['update'] else False
        }
        serializer = serializers.CreateUpdateStaffSerializer(data=data, context=context)
        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data=serializer.errors
            )
        else:
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

    def get(self, request):
        params = request.query_params
        queryset = self.get_filtered_queryset(params)
        if 'dropdown' in params and params['dropdown'] == 'true':
            return self.get_dropdown_list(params)

        if 'download' in params and params['download'] == 'true':
            return self.get_downloadable_link(queryset)

        results = {}
        paginator = Paginator(queryset, 20)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)

        serializer = serializers.StaffDetailsSerializer(page, many=True)
        results['data'] = serializer.data
        results['page'] = page.number
        results['count'] = paginator.count
        return Response(status=status.HTTP_200_OK, data=results)

    @staticmethod
    def get_dropdown_list(params):
        profile_type = params.get('profile_type', None)
        if profile_type is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'message': 'Profile type not found'
            })
        queryset = models.User.objects.filter(
            profile__profile_type=profile_type, is_active=True
        ).select_related('profile')
        serializer = serializers.StaffSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request):
        """
        Deactivates a student account
        1. Deactivate user
        2. Deactivate profile
        3. Deactivate student info
        """
        params = request.query_params
        id = params.get('id', None)
        if id is None:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data='ID is required.'
            )
        try:
            user = models.User.objects.get(id=id)
        except:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data='Invalid ID.'
            )

        user.is_active = False
        user.save()

        profile = user.profile
        profile.is_active = False
        profile.save()

        info = profile.staff_info
        info.is_active = False
        info.save()

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def get_downloadable_link(queryset):
        timestamp = datetime.datetime.now().strftime("%f")
        file_name = f'staff_{timestamp}.csv'
        with open(os.path.join(settings.BASE_DIR, f'downloadables/{file_name}'), mode='w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow([
                'Full Name', 'Date Hired', 'Designation', 'Contact', 'Address'
            ])
            for profile in queryset:
                writer.writerow(StaffAPIView.get_csv_row(profile))
        return Response(file_name, status=status.HTTP_200_OK)

    @staticmethod
    def get_csv_row(profile):
        return [
            profile.fullname,
            profile.staff_info.date_hired.strftime('%d-%m-%Y'),
            profile.staff_info.designation,
            profile.contact,
            profile.staff_info.address,
        ]

    @staticmethod
    def get_filtered_queryset(params):
        filter_serializer = serializers.StaffFilterSerializer(data=params)
        if not filter_serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=filter_serializer.errors
            )

        queryset = models.Profile.objects.filter(
            is_active=True, staff_info_id__isnull=False,
        )

        if 'search_term' in params and len(params['search_term']) > 0:
            q = params['search_term']
            queryset = queryset.filter(
                Q(fullname__icontains=q),
            )

        return queryset
