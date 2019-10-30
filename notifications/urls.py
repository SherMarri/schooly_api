from django.urls import include, path
from rest_framework.routers import DefaultRouter
from notifications import views
notifications_router = DefaultRouter()
notifications_router.register('', views.NotificationViewSet, basename='notifications')


urlpatterns = [
    path('', include(notifications_router.urls)),
]