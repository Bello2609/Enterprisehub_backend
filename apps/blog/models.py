# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.


class PostCategory(models.Model):
    name = models.CharField(max_length=25)
    date = models.DateField(auto_now_add=True)

    def __str__(self):

        return self.name


class NewPost(models.Model):
    category = models.ForeignKey(PostCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    image = models.ImageField()
    content = RichTextField()
    publish = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_edited = models.DateTimeField(blank=True, null=True)
    edited_by = models.ForeignKey(User, related_name='edited_by', null=True, blank=True, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, max_length=254)

    class Meta:
        permissions = (
            ('approve_post', 'Can approve post'),
        )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, *args, **kwargs):

        self.slug = slugify(self.title)
        super(NewPost, self).save(*args, **kwargs)

    def __str__(self):

        return self.title
