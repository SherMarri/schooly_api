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
    url(r'^students/downloadcsv',
        view=views.download_students_csv,
        name='students-download-csv'
    ),
    url(r'^staff/downloadcsv',
        view=views.download_staff_csv,
        name='staff-download-csv'
    ),
    path('students/',
        view=views.StudentAPIView.as_view(),
        name='students'
    ),
    path('staff/',
        view=views.StaffAPIView.as_view(),
        name='staff'
    ),
]