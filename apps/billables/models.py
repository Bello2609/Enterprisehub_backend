# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from ..members.models import Member
from ..staff.models import StaffModel
from ..facility.models import Facility
# Create your models here.


IncomeType = (
    (1, 'membership'),
    (2, 'unit_payment'),

)


class Income(models.Model):
    income_type = models.IntegerField(choices=IncomeType)
    amount = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    trans_id = models.IntegerField()
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)


class CashIn(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateField(auto_now_add=True)


class Debit(models.Model):
    trans_id = models.IntegerField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    staff = models.ForeignKey(StaffModel, blank=True, null=True, on_delete=models.CASCADE)
    remarks = models.CharField(max_length=200)


class Credit(models.Model):
    Payment_Mode = (
        (1, 'POS'),
        (2, 'Transfer'),
        (3, 'Online'),
    )
    facility = models.ForeignKey(Facility, blank=True, null=True, on_delete=models.CASCADE)
    trans_id = models.IntegerField(primary_key=True)
    member = models.ForeignKey(Member, blank=True, null=True, on_delete=models.CASCADE)
    guest_name = models.CharField(max_length=200, blank=True, null=True)
    guest_phone = models.CharField(max_length=15, blank=True, null=True)
    amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    staff = models.ForeignKey(StaffModel, blank=True, null=True, on_delete=models.CASCADE)
    payment_mode = models.IntegerField(choices=Payment_Mode)
    comment = models.CharField(max_length=254)
    sagamy_trans_id = models.IntegerField()
    is_reversed = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ('credit_self', 'Can Credit Self'),
            ('credit_member', 'Can Credit Member'),
        )


class WalletBalance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.IntegerField()


class TransactionLog(models.Model):
    Trans_Type = (
        (1, 'Debit'),
        (2, 'Credit'),
        (3, 'Delete'),
        (4, 'Edit'),
    )
    date = models.DateTimeField(auto_now_add=True)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    staff = models.ForeignKey(StaffModel, on_delete=models.CASCADE)
    trans_type = models.IntegerField(choices=Trans_Type)
    trans_id = models.CharField(max_length=20)
    log = models.TextField()

