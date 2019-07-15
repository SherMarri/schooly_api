from django.contrib import admin
from common import models


class ConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')


admin.site.register(models.Config, ConfigAdmin)