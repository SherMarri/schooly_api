from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from academics import views

router = DefaultRouter()
router.register('subjects', views.SubjectViewSet, basename='academics-subjects')
router.register('grades', views.GradeViewSet, basename='academics-grades')
router.register('sections', views.SectionViewSet, basename='academics-sections')
router.register('assessments', views.AssessmentViewSet, basename='academics-sections')


urlpatterns = [
    path('', include(router.urls)),
]
