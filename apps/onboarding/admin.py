# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import GalleryCat, GalleryPicture

# Register your models here.

admin.site.register(GalleryCat),
admin.site.register(GalleryPicture),
