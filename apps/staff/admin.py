# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import StaffType, StaffModel

# Register your models here.

admin.site.register(StaffType)
admin.site.register(StaffModel)
