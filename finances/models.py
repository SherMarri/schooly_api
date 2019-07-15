from django.db import models

from accounts.models import User
from common.models import BaseModel


DEBIT = 1
CREDIT = 2

class Account(BaseModel):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(max_length=512, null=True, blank=True)
    balance = models.FloatField(default=0)
    is_default = models.NullBooleanField(null=True, blank=True)
    

class TransactionCategory(BaseModel):

    TypeChoices = (
        (DEBIT, 'Income'),
        (CREDIT, 'Expense')
    )

    name = models.CharField(max_length=20)
    description = models.TextField(max_length=512, null=True, blank=True)
    category_type = models.IntegerField(choices=TypeChoices)

    class Meta:
        verbose_name_plural = 'Transaction Categories'

    def __str__(self):
        return self.name


class Transaction(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    description = models.TextField(max_length=512, null=True, blank=True)
    category = models.ForeignKey(TransactionCategory, on_delete=models.CASCADE,
        related_name='transactions')
    amount = models.FloatField()
    account_balance = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
        related_name='created_transactions')
    
    TypeChoices = (
        (DEBIT, 'Debit'),
        (CREDIT, 'Credit')
    )
    transaction_type = models.IntegerField(choices=TypeChoices)
    

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
    paid = models.FloatField(default=0, null=True, blank=True)
    discount = models.FloatField(default=0, null=True, blank=True)
    due_date = models.DateField()
    paid_at = models.DateTimeField(null=True, blank=True)
    paid_by = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(max_length=128, null=True, blank=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                    related_name='received_challans', blank=True)

    def __str__(self):
        return 'Challan for Student ID: {0}'.format(self.student.id)
