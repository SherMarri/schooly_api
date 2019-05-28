from django.contrib import admin

from structure import models


class GradeAdmin(admin.ModelAdmin):
    list_display = ('name',)


class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade')


admin.site.register(models.Grade, GradeAdmin)
admin.site.register(models.Section, SectionAdmin)
