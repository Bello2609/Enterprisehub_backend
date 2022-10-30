# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Facility)
admin.site.register(Category)
admin.site.register(Unit)
admin.site.register(Information)
