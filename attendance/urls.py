from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from attendance import views

router = DefaultRouter()
router.register('daily', views.DailyStudentAttendanceViewSet, basename='student-attendances-daily')

urlpatterns = [
    path('', include(router.urls)),
]
