# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from .validator import FileValidator
import os
from django.dispatch import receiver
# Create your models here.


class MembershipType(models.Model):
    name = models.CharField(max_length=254)
    validity = models.IntegerField()
    before_tax = models.IntegerField()
    amount = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    tax = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.tax = self.before_tax * 7.5 / 100
        self.amount = self.before_tax + self.tax

        super(MembershipType, self).save()

    def __str__(self):
        return "%s - (%s)" % (self.name, self.amount)


class Member(models.Model):
    validate_file = FileValidator(max_size=5242880,
                                  content_types=('image/jpeg', 'application/pdf', 'image/png', 'application/mp4',
                                                 'video/mp4', 'audio/mpeg',
                                                 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                                 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                                 'application/vnd.ms-excel', 'text/plain',))

    GENDER = (
        ('M', 'Male'),
        ('F', 'Female')
    )

    member_id = models.AutoField(unique=True, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=11)
    address = models.TextField()
    type = models.ForeignKey(MembershipType, on_delete=models.CASCADE)
    upgrade_type = models.ForeignKey(MembershipType, related_name='upgrade_type', null=True, blank=True, on_delete=models.CASCADE)
    date_joined = models.DateField(default=timezone.now())
    approve_date = models.DateField(blank=True, null=True)
    last_pay_date = models.DateTimeField(blank=True, null=True)
    expire_date = models.DateField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True)
    username = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=False)
    validated = models.BooleanField(default=False)
    is_activated = models.BooleanField(default=False)
    business_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    cac = models.FileField(null=True, blank=True, validators=[validate_file])
    valid_id = models.FileField(validators=[validate_file])
    accept_tc = models.BooleanField(blank=False, null=False)
    gender = models.CharField(choices=GENDER, max_length=1)

    class Meta:
        permissions = (
            ('activate_member_account', 'Can Activate Member Account'),
            ('activate_member', 'Can Activate Member'),
            ('deactivate_member', 'Can De-Activate Member'),

        )

    def __str__(self):

        return '%s-(%s %s)' % (self.business_name, self.last_name, self.first_name)


class PaymentResources(models.Model):
    amount = models.IntegerField()
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    status = models.BooleanField()
    date = models.DateField(auto_now_add=True)
    ref_id = models.CharField(unique=True, max_length=254)

    def __str__(self):

        return self.member


class CentralDatabase(models.Model):
    validate_file = FileValidator(max_size=5242880,
                                  content_types=('image/jpeg', 'application/pdf', 'image/png', 'application/mp4',
                                                 'video/mp4', 'audio/mpeg',
                                                 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                                 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                                 'application/vnd.ms-excel', 'text/plain',))

    title = models.CharField(max_length=200)
    docs = models.FileField(upload_to='central_database', validators=[validate_file])
    owned_by = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)


@receiver(models.signals.post_delete, sender=CentralDatabase)
def delete_file_on_object_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `file1` object is deleted.
    """
    if instance.docs:
        if os.path.isfile(instance.docs.path):
            os.remove(instance.docs.path)


@receiver(models.signals.pre_save, sender=CentralDatabase)
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
        old_file = CentralDatabase.objects.get(id=instance.id).docs
    except CentralDatabase.DoesNotExist:
        return False

    new_file = instance.docs
    if not old_file == new_file:
        try:
            os.path.isfile(old_file.path)
            os.remove(old_file.path)
        except ValueError:
            pass