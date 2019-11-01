"""schooly_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from common import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url('api/v1/users/', include('accounts.urls')),
    url('api/v1/finance/', include('finances.urls')),
    url('api/v1/academics/', include('academics.urls')),
    url('api/v1/attendance/', include('attendance.urls')),
    url('api/v1/notifications/', include('notifications.urls')),
    url('api/v1/download_csv',
        view=views.download_csv,
        name='download-csv'
        ),
]
