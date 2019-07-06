from django.db import models

from accounts.models import User
from common.models import BaseModel


class IncomeCategory(BaseModel):
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=512, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Income Categories'

    def __str__(self):
        return self.name


class IncomeItem(BaseModel):
    title = models.CharField(max_length=128)
    category = models.ForeignKey(IncomeCategory, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='items')
    description = models.TextField(max_length=512, null=True, blank=True)
    amount = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return self.title


class ExpenseCategory(BaseModel):
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=512, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Expense Categories'

    def __str__(self):
        return self.name


class ExpenseItem(BaseModel):
    title = models.CharField(max_length=128)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='items')
    description = models.CharField(max_length=512, null=True, blank=True)
    amount = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return self.title


class FeeStructure(BaseModel):
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=512, null=True, blank=True)
    break_down = models.TextField(max_length=2048)
    total = models.FloatField()

    def __str__(self):
        return self.name


class FeeChallan(BaseModel):
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                related_name='challans')
    break_down = models.TextField(max_length=2048)
    total = models.FloatField()
    paid = models.FloatField(null=True, blank=True)
    discount = models.FloatField(default=0, null=True, blank=True)
    due_date = models.DateField()
    paid_at = models.DateTimeField(null=True, blank=True)
    paid_by = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(max_length=128, null=True, blank=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                    related_name='received_challans', blank=True)

    def __str__(self):
        return 'Challan for Student ID: {0}'.format(self.student.id)
