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
]