# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView, TemplateView
from .models import StaffModel, ActivityLog
from ..account.models import UserType
from .forms import CreateStaffForm, UpdateStaffForm, UpdateSelfForm
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.core.mail import EmailMessage
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
# Create your views here.


class NewStaff(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = StaffModel
    form_class = CreateStaffForm
    template_name = 'backend/staff/new_staff.html'
    success_url = reverse_lazy('new_staff')
    raise_exception = True
    permission_required = 'staff.add_staffmodel'

    def form_valid(self, form):
        with transaction.atomic():
            password = User.objects.make_random_password()
            new_user = User.objects.create_user(
                username=form.instance.username,
                password=password,
                email=form.instance.email,
                first_name=form.instance.first_name,
                last_name=form.instance.last_name,
            )
            create_account_type = UserType.objects.create(account_type=2, user_id=new_user.id)
            new_user.save()

            group, created = Group.objects.get_or_create(name='staff')
            group.user_set.add(new_user.id)

            form.instance.user_id = new_user.id
            create_account_type.save()

            create_log = ActivityLog.objects.create(
                log_text='%s created a new staff (%s)' % (self.request.user.username, form.instance.username),
                user_id=self.request.user.id
            )
            create_log.save()
            message = ('Hi %s, <br /> Welcome to Enterprise Hubs. Please login with the below details <br /><br />'
                       'username: %s <br />password: %s') % (form.instance.username, form.instance.username, password)
            subject = 'Welcome to Enterprise Hubs'
            to_email = form.instance.email
            send_mail = EmailMessage(subject, message, to=[to_email])
            send_mail.content_subtype = 'html'
            send_mail.send()

            messages.success(self.request, 'You successfully created a new staff account')
        return super(NewStaff, self).form_valid(form)


class StaffList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = 'backend/staff/all_staff.html'
    model = StaffModel
    raise_exception = True
    permission_required = 'staff.view_staff_list'

    def get_context_data(self, **kwargs):
        context = super(StaffList, self).get_context_data(**kwargs)
        get_staff = StaffModel.objects.get(user_id=self.request.user.id)
        if get_staff.is_oga is True:
            context['staff_list'] = StaffModel.objects.filter(user__is_staff=False)
        else:
            context['staff_list'] = StaffModel.objects.filter(facility_id=get_staff.facility_id, user__is_staff=False)
        return context


class StaffDetails(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = StaffModel
    template_name = 'backend/staff/staff_detail.html'
    pk_url_kwarg = 'staff_id'
    permission_required = 'staff.view_staff_list'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super(StaffDetails, self).get_context_data(**kwargs)
        try:
            context['activity_log'] = ActivityLog.objects.filter(user_id=self.object.user_id).order_by('-id')[:150]
        except ActivityLog.DoesNotExist:
            context['activity_log'] = None

        return context


class UpdateSelf(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'backend/staff/update_staff_self.html'
    model = StaffModel
    form_class = UpdateSelfForm
    pk_url_kwarg = 'staff_id'
    raise_exception = True

    def test_func(self):
        self.object = self.get_object()
        staff_id = StaffModel.objects.get(user_id=self.request.user.id)
        if self.object.id == staff_id.id:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse_lazy('staff_details', args=[self.object.facility_id, self.object.id ])

    def form_valid(self, form):
        messages.success(self.request, 'You have successfully updated your profile')
        return super(UpdateSelf, self).form_valid(form)


class UpdateStaff(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'backend/staff/new_staff.html'
    model = StaffModel
    form_class = UpdateStaffForm
    success_url = reverse_lazy('all_staff')
    pk_url_kwarg = 'staff_id'
    raise_exception = True
    permission_required = 'staff.change_staffmodel'

    def form_valid(self, form):
        create_log = ActivityLog.objects.create(
            log_text='%s updated a staff account (%s)' % (self.request.user.username, self.object.username),
            user_id=self.request.user.id
        )
        create_log.save()
        messages.success(self.request, 'You successfully updated a new staff account')
        return super(UpdateStaff, self).form_valid(form)


@login_required()
@permission_required(perm='staff.de_activate_staff', raise_exception=True)
def deactivate_staff(request, user_id):
    get_user = User.objects.get(id=user_id)
    get_user.is_active = False
    get_user.save()

    create_log = ActivityLog.objects.create(
        log_text='%s deactivated a staff account (%s)' % (request.user.username, get_user.username),
        user_id=request.user.id
    )
    create_log.save()

    messages.success(request, 'You have successfully deactivated a staff account')
    return redirect('all_staff')


@login_required()
@permission_required(perm='staff.activate_staff', raise_exception=True)
def activate_staff(request, user_id):
    get_user = User.objects.get(id=user_id)
    get_user.is_active = True
    get_user.save()

    create_log = ActivityLog.objects.create(
        log_text='%s reactivated a staff account (%s)' % (request.user.username, get_user.username),
        user_id=request.user.id
    )
    create_log.save()

    messages.success(request, 'You have successfully reactivated a staff account')
    return redirect('all_staff')


class StaffActivityLog(TemplateView):
    template_name = 'backend/staff/staff_activity_log.html'

    def get_context_data(self, **kwargs):
        context = super(StaffActivityLog, self).get_context_data(**kwargs)
        context['staff_activity'] = ActivityLog.objects.filter(user__is_staff=False).order_by('-action_time')

        return context
