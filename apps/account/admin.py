# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import UserType, BankAcc, HubGL

# Register your models here.

admin.site.register(UserType)
admin.site.register(BankAcc)
admin.site.register(HubGL)
