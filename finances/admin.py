from django.contrib import admin

from finances import models


class IncomeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


class IncomeItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'amount')
    list_display_links = ('category',)


class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ExpenseItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'amount')
    list_display_links = ('category',)


class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'total')


class FeeChallanAdmin(admin.ModelAdmin):
    list_display = ('student', 'structure', 'due_date', 'paid', 'discount', 'total')
    list_display_links = ('student', 'structure',)


admin.site.register(models.IncomeCategory, IncomeCategoryAdmin)
admin.site.register(models.IncomeItem, IncomeItemAdmin)
admin.site.register(models.ExpenseCategory, ExpenseCategoryAdmin)
admin.site.register(models.ExpenseItem, ExpenseItemAdmin)
admin.site.register(models.FeeStructure, FeeStructureAdmin)
admin.site.register(models.FeeChallan, FeeChallanAdmin)
