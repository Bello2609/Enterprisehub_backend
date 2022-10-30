# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from ..facility.models import Facility
from django.contrib.auth.models import User

# Create your models here.


class StaffType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class StaffModel(models.Model):
    username = models.CharField(max_length=15)
    email = models.EmailField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=11)
    address = models.TextField()
    image = models.ImageField(null=True, blank=True)
    staff_type = models.ForeignKey(StaffType, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    is_oga = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        permissions = (
            ('view_staff_list', 'Can view staff list'),
            ('de_activate_staff', 'Can deactivate staff'),
            ('activate_staff', 'Can activate staff'),
        )

    def __str__(self):
        return self.username


class ActivityLog(models.Model):
    action_time = models.DateTimeField(auto_now_add=True)
    log_text = models.CharField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
