from django.urls import path, include
from rest_framework.routers import DefaultRouter

from structure import views

router = DefaultRouter()
router.register('grades', views.GradeViewSet, basename='structure-grades')

urlpatterns = [
    path('', include(router.urls)),
]
