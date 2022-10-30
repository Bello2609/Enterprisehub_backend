# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from ..facility.models import Category
from django.contrib.auth.models import User

# Create your models here.


AccountType = (
    (1, 'member'),
    (2, 'staff'),
)


class UserType(models.Model):
    account_type = models.IntegerField(choices=AccountType)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class BankAcc(models.Model):
    name = models.CharField(max_length=20)
    account_no = models.IntegerField()

    def __str__(self):
        return self.name


class HubGL(models.Model):
    category = models.OneToOneField(Category, on_delete=models.CASCADE)
    acc_no = models.CharField(max_length=4)

    def __str__(self):
        return self.category.cat_name



