# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from ..bookings.models import Bookings

# Create your models here.


class GuestPaymentResource(models.Model):
    booking = models.ForeignKey(Bookings, on_delete=models.CASCADE)
    amount = models.IntegerField()
    status = models.BooleanField()
    date = models.DateField(auto_now_add=True)
    ref_id = models.CharField(unique=True, max_length=254)


class GalleryCat(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):

        return self.name


class GalleryPicture(models.Model):
    category = models.ForeignKey(GalleryCat, on_delete=models.CASCADE)
    image = models.ImageField()

    def __str__(self):

        return self.image.name


class Testimonials(models.Model):
    image = models.ImageField(upload_to="Testimonial", blank=True, null=True)
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    content = models.TextField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):

        return self.name


class ClientLogo(models.Model):
    client_name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='Client_Logo')
    url = models.URLField(blank=True, null=True)

    def __str__(self):

        return self.client_name


class FrontDesk(models.Model):
    PURPOSE = (
        ('official', 'Official'),
        ('visiting', 'Visiting'),
        ('event', 'Event'),
        ('others', 'Others'),

    )
    HOW = (
        ('facebook', 'Facebook'),
        ('linkedin', 'Linkedin'),
        ('recommendation', 'Recommendation'),
        ('billboard', 'Billboards')
    )
    name = models.CharField(max_length=50)
    business_name = models.CharField(max_length=254, blank=True, null=True)
    position = models.CharField(max_length=254, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    whom_to_see = models.CharField(blank=True, null=True, max_length=50)
    purpose = models.CharField(choices=PURPOSE, max_length=50)
    phone = models.CharField(max_length=11, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    how = models.CharField(choices=HOW, max_length=50, blank=True, null=True)



