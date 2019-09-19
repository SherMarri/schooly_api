from django.contrib import admin

from accounts import models


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fullname', 'profile_type')


admin.site.register(models.Profile, ProfileAdmin)