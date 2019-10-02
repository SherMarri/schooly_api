from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from academics import views

router = DefaultRouter()
router.register('subjects', views.SubjectViewSet, basename='subjects')
router.register('grades', views.GradeViewSet, basename='structure-grades')



urlpatterns = [
    path('', include(router.urls)),
]
