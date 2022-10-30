# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Services, ServiceCategory
from .forms import NewServiceFormSet
from django.views import generic
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import transaction
from .models import ServiceBooking, BookedServices
from .models import Member
from ..facility.models import Facility
from ..billables.models import WalletBalance
from ..account.models import UserType
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required
from ..staff.models import StaffModel
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from ..billables.models import Debit
import random
from ..staff.models import ActivityLog
from ..members.views import post_credit_post_sagamy
# Create your views here.


class SelectService(LoginRequiredMixin, generic.TemplateView):
    template_name = 'backend/services/select_services.html'

    def get_context_data(self, **kwargs):
        context = super(SelectService, self).get_context_data(**kwargs)
        context['all_services'] = ServiceCategory.objects.all()
        context['a_type'] = self.kwargs['a_type']
        return context


@login_required()
def service_payment(request, service_book_id, member_id):
    if member_id is not None:
        booked_service = BookedServices.objects.filter(service_booking_id=service_book_id)
        total_amount = sum(booked_service.values_list('amount_payable', flat=True))
        wallet_balance = WalletBalance.objects.get(member_id=member_id)
        if wallet_balance.amount - total_amount < 0:
            return False
        else:
            wallet_balance.amount -= total_amount
            wallet_balance.save()
            update_booking = ServiceBooking.objects.get(id=service_book_id)
            update_booking.payment_status = True
            update_booking.payment_date = datetime.now()
            update_booking.save()
            return True
    else:
        update_booking = ServiceBooking.objects.get(id=service_book_id)
        update_booking.payment_status = True
        update_booking.is_completed = True
        update_booking.payment_date = datetime.now()
        update_booking.save()
        return True


@login_required()
@permission_required(perm='services.delete_servicebooking', raise_exception=True)
def service_delete(request, service_book_id):
    booked_service = BookedServices.objects.filter(service_booking_id=service_book_id)
    for item in booked_service:
        item.delete()
    get_service_booking = ServiceBooking.objects.get(id=service_book_id)
    get_service_booking.delete()
    log = ActivityLog.objects.create(
        log_text='%s delete service with ID of %s' % (request.user.username, service_book_id),
        user_id=request.user.id

    )
    log.save()
    messages.success(request, 'Action was successful, service has been deleted')
    return redirect('service_booking_list')


@login_required()
def service_pay_later(request, service_book_id, member_id):
    if member_id is not 0:
        if service_payment(request, service_book_id, member_id) is True:
            booked_service = BookedServices.objects.filter(service_booking_id=service_book_id)
            total_amount = sum(booked_service.values_list('amount_payable', flat=True))
            debit_create = Debit.objects.create(
                trans_id=random.randrange(1, 1234567890, 5),
                member_id=member_id,
                amount=total_amount,
                remarks='Debit transaction for service with ID #%s' % service_book_id

            )
            debit_create.save()
            messages.success(request, 'Success, Your payment has been confirmed')
        else:
            messages.warning(request, 'Error, Insufficient balance')

    return redirect('view_booked_services', service_book_id)


@login_required()
@permission_required(perm='services.delete_servicebooking', raise_exception=True)
def complete_service(request, service_book_id):
    get_service_booking = ServiceBooking.objects.get(id=service_book_id)
    get_service_booking.is_completed = True
    get_service_booking.complete_date = datetime.now()
    get_service_booking.save()
    log = ActivityLog.objects.create(
        log_text='%s mark service with ID of %s as completed' % (request.user.username, service_book_id),
        user_id=request.user.id

    )
    log.save()
    message = render_to_string('emails/new_service_booking.html', {
        'user': get_service_booking.member.first_name + ' ' + get_service_booking.member.last_name,
        'service_id': service_book_id,
        'type': 'completed'
    })
    mail_subject = 'Enterprise Hubs, service completed'
    to_email = get_service_booking.member.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.content_subtype = 'html'
    send_email.send()
    messages.success(request, 'Action was successful, service has been rendered as complete')
    return redirect('service_booking_list')


@login_required()
def service_booking(request, service_cat_id, a_type):
    facility = Facility.objects.all()
    member = Member.objects.all()
    service_details = ServiceCategory.objects.get(id=service_cat_id)
    if request.method == 'POST':
        formset = NewServiceFormSet(request.POST, form_kwargs={'service_cat_id': service_cat_id})
        if formset.is_valid():
            with transaction.atomic():

                if 'member_id' in request.POST:
                    member_id = request.POST['member_id']
                    facility_id = StaffModel.objects.get(username=request.user.username).facility_id
                    service_create = ServiceBooking.objects.create(
                        member_id=member_id,
                        payment_status=False,
                        service_cat_id=service_cat_id,
                        is_completed=False,
                        facility_id=facility_id,
                    )
                else:
                    if a_type == 'member':
                        member_id = Member.objects.get(username=request.user.username).member_id
                        facility_id = request.POST['facility_id']

                        service_create = ServiceBooking.objects.create(
                            member_id=member_id,
                            payment_status=False,
                            service_cat_id=service_cat_id,
                            is_completed=False,
                            facility_id=facility_id,
                        )
                    else:
                        member_id = None
                        facility_id = StaffModel.objects.get(username=request.user.username).facility_id
                        service_create = ServiceBooking.objects.create(
                            guest_name=request.POST['customer_name'],
                            guest_phone=request.POST['customer_phone'],
                            payment_status=False,
                            service_cat_id=service_cat_id,
                            is_completed=False,
                            facility_id=facility_id
                        )

                # Upload script if printable file
                if 'print_file' in request.FILES:
                    printable_file = request.FILES['print_file']
                    fs = FileSystemStorage()
                    file_name = fs.save(printable_file.name, printable_file)
                    printable_url = fs.url(file_name)
                    service_create.printable = printable_url

                if 'is_remarkable' in request.POST:
                    service_create.Desc = request.POST['is_remarkable']

                service_create.save()

                for form in formset:
                    form = BookedServices.objects.create(
                        service_booking_id=service_create.id,
                        service_id=form.instance.service.id,
                        quantity=form.instance.quantity,
                        amount_payable=Services.objects.get(id=form.instance.service.id).amount,
                    )
                    form.save()

                service_pay_status = service_payment(request, service_create.id, member_id)
                booked_service = BookedServices.objects.filter(service_booking_id=service_create.id)
                total_amount = sum(booked_service.values_list('amount_payable', flat=True))

                if service_pay_status is True and a_type == 'member':
                    get_member = Member.objects.get(member_id=member_id)

                    debit_create = Debit.objects.create(
                        trans_id=random.randrange(1, 1234567890, 5),
                        member_id=member_id,
                        amount=total_amount,
                        remarks='Debit transaction for service with ID #%s' % service_create.id

                    )
                    debit_create.save()

                    if service_details.is_billable:

                        # Printing Sagamy
                        if service_cat_id == '1':
                            post_credit_post_sagamy(
                                request,
                                facility_id=facility_id,
                                ref_id=random.randrange(1, 1234567890, 5),
                                guest_name=None,
                                guest_phone=None,
                                amount=total_amount,
                                pay_mode=3,
                                account='3108',
                                member_id=None,
                                debit_account='2121',
                                trans_type='%s paid NGN %s, for a service with ID %s ' % (get_member.username,
                                                                                          total_amount, service_cat_id)
                            )
                        # Cafeteria Sagamy
                        elif service_cat_id == '3':
                            post_credit_post_sagamy(
                                request,
                                facility_id=facility_id,
                                ref_id=random.randrange(1, 1234567890, 5),
                                guest_name=None,
                                guest_phone=None,
                                amount=total_amount,
                                pay_mode=3,
                                account='3113',
                                member_id=None,
                                debit_account='2121',
                                trans_type='%s paid NGN %s, for a service with ID %s ' % (get_member.username,
                                                                                          total_amount, service_cat_id)
                            )

                    message = render_to_string('emails/new_service_booking.html', {
                        'user': get_member.first_name + ' ' + get_member.last_name,
                        'service_id': service_create.id,
                        'amount': total_amount,
                        'service_paid': service_pay_status,
                        'type': 'new'
                    })
                    mail_subject = 'Welcome Enterprise Hubs, New Service Booking'
                    to_email = get_member.email
                    send_email = EmailMessage(mail_subject, message, to=[to_email])
                    send_email.content_subtype = 'html'
                    send_email.send()

                    messages.success(request, 'Your services has been booked and amount debited from your wallet')
                elif service_pay_status is True and a_type == 'guest':
                    if service_details.is_billable:

                        # Printing Sagamy
                        if service_cat_id == '1':
                            post_credit_post_sagamy(
                                request,
                                facility_id=facility_id,
                                ref_id=random.randrange(1, 1234567890, 5),
                                guest_name=request.POST['customer_name'],
                                guest_phone=request.POST['customer_phone'],
                                amount=total_amount,
                                pay_mode=3,
                                account='3108',
                                member_id=0,
                                debit_account='2121',
                                trans_type='Guest paid NGN %s, for a service with ID %s ' % (total_amount, service_cat_id)
                            )
                        # Cafeteria Sagamy
                        elif service_cat_id == '3':
                            post_credit_post_sagamy(
                                request,
                                facility_id=facility_id,
                                ref_id=random.randrange(1, 1234567890, 5),
                                guest_name=request.POST['customer_name'],
                                guest_phone=request.POST['customer_phone'],
                                amount=total_amount,
                                pay_mode=3,
                                account='3113',
                                member_id=0,
                                debit_account='2121',
                                trans_type='Guest paid NGN %s, for a service with ID %s ' % (total_amount, service_cat_id)
                            )
                        messages.success(request, 'Guest service has been completed successfully')
                else:
                    messages.warning(request, 'Your services has been booked, but you seem to have insufficient amount,'
                                              'Please kindly fund your wallet to complete this transaction')

        return redirect('view_booked_services', service_create.id)
    else:
        formset = NewServiceFormSet(form_kwargs={'service_cat_id': service_cat_id})
    return render(request, 'backend/services/new_service.html', {'formset': formset, 'service_cat_id': service_cat_id,
                                                                 'facility': facility, 'member': member,
                                                                 'service_details': service_details, 'a_type': a_type})


class ServiceBookingList(LoginRequiredMixin, generic.ListView):
    template_name = 'backend/services/all_services.html'
    model = ServiceBooking

    def get_context_data(self, **kwargs):
        context = super(ServiceBookingList, self).get_context_data(**kwargs)
        get_user = self.request.user.id
        if UserType.objects.get(user_id=get_user).account_type is 2:
            context['object_list'] = ServiceBooking.objects.all().order_by('-id')
        else:
            get_member = Member.objects.get(username=self.request.user.username)
            context['object_list'] = ServiceBooking.objects.filter(member_id=get_member).order_by('-id')
        return context


class ViewBookedServices(LoginRequiredMixin, UserPassesTestMixin, generic.TemplateView):
    template_name = 'backend/services/service_detail.html'
    raise_exception = True

    def test_func(self):
        user_type = UserType.objects.get(user_id=self.request.user.id)
        if user_type.account_type == 2:
            return True
        else:
            member_id = Member.objects.get(username=self.request.user.username).member_id
            service_id = ServiceBooking.objects.get(id=self.kwargs['service_id']).member_id
            if member_id == service_id:
                return True
            else:
                return False

    def get_context_data(self, **kwargs):
        context = super(ViewBookedServices, self).get_context_data(**kwargs)
        booked_services = BookedServices.objects.filter(service_booking_id=self.kwargs['service_id'])
        context['booked_services'] = booked_services
        context['get_book_details'] = ServiceBooking.objects.get(id=self.kwargs['service_id'])
        context['total_amount'] = sum(booked_services.values_list('amount_payable', flat=True))

        return context


class PrintBookedServices(LoginRequiredMixin, UserPassesTestMixin, generic.TemplateView):
    template_name = 'backend/services/print_booked_services.html'
    raise_exception = True

    def test_func(self):
        user_type = UserType.objects.get(user_id=self.request.user.id)
        if user_type.account_type == 2:
            return True
        else:
            member_id = Member.objects.get(username=self.request.user.username).member_id
            service_id = ServiceBooking.objects.get(id=self.kwargs['service_id']).member_id
            if member_id == service_id:
                return True
            else:
                return False

    def get_context_data(self, **kwargs):
        context = super(PrintBookedServices, self).get_context_data(**kwargs)
        booked_services = BookedServices.objects.filter(service_booking_id=self.kwargs['service_id'])
        context['booked_services'] = booked_services
        context['get_book_details'] = ServiceBooking.objects.get(id=self.kwargs['service_id'])
        context['total_amount'] = sum(booked_services.values_list('amount_payable', flat=True))

        return context


