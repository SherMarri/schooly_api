from django.contrib import admin

from academics import models


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)


class SectionSubjectAdmin(admin.ModelAdmin):
    list_display = ('subject', 'section', 'teacher')


admin.site.register(models.Subject, SubjectAdmin)
admin.site.register(models.SectionSubject, SectionSubjectAdmin)