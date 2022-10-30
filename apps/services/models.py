# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from ..members.models import Member
from ..facility.models import Facility

# Create your models here.


class ServiceCategory(models.Model):
    name = models.CharField(max_length=200)
    icon = models.ImageField(upload_to='service_icon')
    is_billable = models.BooleanField()
    is_printable = models.BooleanField()
    is_remarkable = models.BooleanField(default=False)

    def __str__(self):

        return self.name


class Services(models.Model):
    cat_name = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    amount = models.IntegerField(blank=True, null=True)

    def __str__(self):

        return '%s (NGN %s)' % (self.name, self.amount)


class ProfessionalService(models.Model):
    name = models.CharField(max_length=255)
    body = models.TextField()
    image = models.ImageField(upload_to='prof_service')

    def __str__(self):

        return self.name


class ServiceBooking(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, null=True, blank=True, on_delete=models.CASCADE)
    guest_name = models.CharField(max_length=150, blank=True, null=True)
    guest_phone = models.CharField(max_length=11, blank=True, null=True)
    guest_email = models.EmailField(blank=True, null=True)
    service_cat = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    payment_status = models.BooleanField()
    is_completed = models.BooleanField()
    date = models.DateTimeField(auto_now_add=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    complete_date = models.DateTimeField(null=True, blank=True)
    printable = models.FileField(blank=True, null=True)
    Desc = models.TextField(blank=True, null=True)


class BookedServices(models.Model):
    service_booking = models.ForeignKey(ServiceBooking, on_delete=models.CASCADE)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    amount_payable = models.IntegerField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.amount_payable = self.quantity * self.service.amount

        super(BookedServices, self).save()

    def __str__(self):

        return self.service.name
