from django.contrib import admin

from finances import models


class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance')


class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type')


class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'account', 'category', 'amount', 'account_balance'
    )
    list_display_links = ('account', 'category',)


class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'total')


class FeeChallanAdmin(admin.ModelAdmin):
    list_display = ('student', 'due_date', 'paid', 'discount', 'total')
    list_display_links = ('student',)


admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.TransactionCategory, TransactionCategoryAdmin)
admin.site.register(models.Transaction, TransactionAdmin)
admin.site.register(models.FeeStructure, FeeStructureAdmin)
admin.site.register(models.FeeChallan, FeeChallanAdmin)
