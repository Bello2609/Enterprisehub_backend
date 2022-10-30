# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import uuid
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.contrib.auth.models import User
from ..members.validator import FileValidator
import os
from django.dispatch import receiver
import os
from django.dispatch import receiver

# Create your models here.


class Facility(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, db_index=True, default=uuid.uuid4, editable=False,
                          verbose_name='Facility ID ')
    name = models.CharField(max_length=50)
    address = models.TextField()

    class Meta:
        permissions = (
            ('can_view_dashboard', 'Can View DashBoard'),
        )

    def __str__(self):

        return self.name


class Category(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    cat_name = models.CharField(max_length=50)
    access_no = models.CharField(max_length=25, blank=True, null=True)

    def __str__(self):

        return self.cat_name


class Unit(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    amount = models.IntegerField()
    validity_period = models.SmallIntegerField()
    restricted = models.BooleanField()

    def __str__(self):

        return f"{self.name} - {self.amount} - {self.category.cat_name} - {self.facility.name}"


class Information(models.Model):
    title = models.CharField(max_length=50)
    content = RichTextField()
    slug = models.SlugField(unique=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, *args, **kwargs):

        self.slug = slugify(self.title)

        super(Information, self).save(*args, **kwargs)

    def __str__(self):

        return self.title


class ResourceCenter(models.Model):
    validate_file = FileValidator(max_size=5242880,
                                  content_types=('image/jpeg', 'application/pdf', 'image/png', 'application/mp4',
                                                 'video/mp4', 'audio/mpeg',
                                                 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                                 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                                 'application/vnd.ms-excel', 'text/plain',))

    is_file = models.BooleanField(blank=True)
    is_video = models.BooleanField(blank=True)
    is_link = models.BooleanField(blank=True)
    video_id = models.CharField(max_length=15, blank=True, null=True)
    doc = models.FileField(blank=True, null=True, validators=[validate_file])
    title = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now=True)
    link = models.URLField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):

        return self.title


@receiver(models.signals.post_delete, sender=ResourceCenter)
def delete_file_on_object_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `file1` object is deleted.
    """
    if instance.doc:
        if os.path.isfile(instance.doc.path):
            os.remove(instance.doc.path)


@receiver(models.signals.pre_save, sender=ResourceCenter)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `files` object is updated
    with new file or cleared.
    """

    if not instance.id:
        return False
    # file 1
    try:
        old_file = ResourceCenter.objects.get(id=instance.id).doc
    except ResourceCenter.DoesNotExist:
        return False

    new_file = instance.doc
    if not old_file == new_file:
        try:
            os.path.isfile(old_file.path)
            os.remove(old_file.path)
        except ValueError:
            pass


