from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from attendance import views

router = DefaultRouter()
router.register('daily', views.DailyStudentAttendanceViewSet, basename='students-attendance-daily')

staff_router = DefaultRouter()
staff_router.register('daily', views.DailyStaffAttendanceViewSet, basename='staff-attendance-daily')

urlpatterns = [
    path('students/', include(router.urls)),
    path('staff/', include(staff_router.urls)),
]
