# -*- coding: utf-8 -*-
from django.db import models
from ..facility.models import Facility, Category, Unit
from ..members.models import Member

# Create your models here.


class Bookings(models.Model):

    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, blank=True, null=True, on_delete=models.CASCADE)
    guest_name = models.CharField(max_length=200, blank=True, null=True)
    guest_email = models.EmailField(blank=True, null=True)
    guest_phone = models.CharField(max_length=11, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    book_from = models.DateField()
    book_to = models.DateField(blank=True, null=True)
    is_secured = models.BooleanField(default=False)
    is_hold = models.BooleanField(default=True)
    is_member = models.BooleanField()
    payable_before_tax = models.DecimalField(decimal_places=2, max_digits=10)
    discount = models.IntegerField(default=0)
    tax = models.DecimalField(decimal_places=2, max_digits=10)
    payable = models.DecimalField(decimal_places=2, max_digits=10)

    class Meta:
        permissions = (
            ('view_all_bookings', 'Can view all bookings'),
            ('approve_bookings', 'Can approve booking'),
        )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        payable = self.amount_payable()
        print(self.discount)
        self.payable_before_tax = payable
        self.tax = payable * 7.5 / 100
        self.payable = (payable + self.tax) - self.discount

        super(Bookings, self).save()

    def amount_payable(self):
        if self.book_to:
            get_days = (self.book_to - self.book_from).days
            payable = self.unit.amount * (get_days + 1)

            return payable
        else:
            payable = self.unit.amount
            return payable


class HeldBookings(models.Model):
    booking = models.ForeignKey(Bookings, on_delete=models.CASCADE)
    date = models.DateField()
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
