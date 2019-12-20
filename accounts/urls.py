from django.conf.urls import url
from django.urls import include, path

from accounts import views

urlpatterns = [
    path('', include('accounts.rest_auth_urls')),
    url(
        'students/autocomplete',
        view=views.StudentsAutocompleteAPIView.as_view(),
        name='students_autocomplete'
    ),
    path('students/<int:user_id>/',
        view=views.StudentDetailsAPIView.as_view(),
        name='student-details'
    ),
    path('students/',
        view=views.StudentAPIView.as_view(),
        name='students'
    ),
    path('staff/',
        view=views.StaffAPIView.as_view(),
        name='staff'
    ),
    path('groups/',
        view=views.GroupAPIView.as_view(),
        name='groups'
    ),
]