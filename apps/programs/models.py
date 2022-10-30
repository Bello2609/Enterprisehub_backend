# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.text import slugify

# Create your models here.


class Programs(models.Model):
    name = models.CharField(max_length=200)
    about = models.TextField()
    image = models.ImageField(upload_to='programs')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    valid = models.BooleanField(default=True)
    capacity = models.IntegerField(blank=True, null=True)
    amount = models.IntegerField()
    slug = models.SlugField(unique=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = slugify(self.name)
        super(Programs, self).save()

    def __str__(self):

        return self.name


class Register(models.Model):
    program = models.ForeignKey(Programs, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    occupation = models.CharField(max_length=200, blank=True, null=True)
    company = models.CharField(max_length=50, blank=True, null=True)
    designation = models.CharField(max_length=50, blank=True, null=True)
    p_status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return '%s - %s' % (self.name, self.program)
