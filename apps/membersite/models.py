# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ckeditor.fields import RichTextField
from django.db import models
from django.utils.text import slugify
from ..members.models import Member
from .validator import FileValidator
from django.contrib.auth.models import User

# Create your models here.


def firm_directory_path(instance, filename):

    return 'member_{0}/{1}'.format(instance.member_id, filename)


class MainSite(models.Model):
    validate_file = FileValidator(max_size=5242880, content_types=('image/jpeg', 'image/png'))
    member = models.OneToOneField(Member, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=firm_directory_path, validators=[validate_file], blank=False, null=True)
    about_us = RichTextField(blank=True, null=True)
    business_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    url_identifier = models.CharField(help_text='www.enterprisehubs.com/your_business_name', max_length=100, unique=True,
                                      blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    facebook = models.CharField(max_length=50, help_text='Facebook Username eg. enterprise_hubs', blank=True, null=True)
    instagram = models.CharField(max_length=50, help_text='Facebook Username eg. enterprise_hubs', blank=True,
                                 null=True)
    linkedin = models.CharField(max_length=50, help_text='Facebook Username eg. enterprise_hubs', blank=True, null=True)
    google_plus = models.CharField(max_length=50, help_text='Facebook Username eg. enterprise_hubs', blank=True,
                                   null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, *args, **kwargs):

        self.slug = slugify(self.url_identifier)
        member_details = Member.objects.get(member_id=self.member_id)
        self.business_name = member_details.business_name
        self.phone = member_details.phone
        self.email = member_details.email

        super(MainSite, self).save(*args, **kwargs)

    def __str__(self):

        return self.business_name


class Portfolio(models.Model):
    validate_file = FileValidator(max_size=5242880, content_types=('image/jpeg', 'image/png'))
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    client = models.CharField(max_length=25, blank=True, null=True)
    desc = models.TextField(help_text='Describe what technology/tools used in achieving clients goal')
    image = models.ImageField(upload_to=firm_directory_path, null=False, blank=False, validators=[validate_file])
