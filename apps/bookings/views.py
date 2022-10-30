# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, TemplateView
from .models import Bookings, HeldBookings
from .forms import MemberBookingForm
from django.contrib import messages
from django.db import transaction
from ..billables.models import WalletBalance, Debit, Income, CashIn, TransactionLog
from ..staff.models import ActivityLog
from ..members.models import Member
from django.shortcuts import redirect
from ..facility.models import Category, Unit
from ..account.models import UserType
from django.shortcuts import render
from datetime import timedelta, datetime
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import permission_required
from ..account.models import BankAcc
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from ..billables.views import post_credit_post_sagamy
from ..staff.models import StaffModel
from ..account.models import HubGL

# Create your views here.


class MemberBookingView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Bookings
    template_name = 'backend/bookings/new_bookings.html'
    form_class = MemberBookingForm
    success_url = reverse_lazy('member_booking')
    raise_exception = True
    permission_required = 'bookings.add_bookings'

    def form_valid(self, form):
        with transaction.atomic():
            book_date = datetime.strptime(str(form.instance.book_from), '%Y-%m-%d')
            form.instance.is_member = True
            try:
                get_member = Member.objects.get(username=self.request.user.username)
                form.instance.member_id = get_member.member_id
            except Member.DoesNotExist:
                pass

            form.save()

            if self.request.POST.get('book_to'):
                end_date = datetime.strptime(str(form.instance.book_to), '%Y-%m-%d')
                delta = end_date - book_date

                for i in range(delta.days + 1):

                    held_book_range = HeldBookings.objects.create(
                        booking_id=form.instance.id,
                        date=book_date + timedelta(i),
                        unit_id=form.instance.unit_id
                    )
                    held_book_range.save()
            else:
                held_book_range = HeldBookings.objects.create(
                    booking_id=form.instance.id,
                    date=book_date,
                    unit_id=form.instance.unit_id
                )
                held_book_range.save()
            messages.success(self.request, 'Your bookings has been created')

        return super(MemberBookingView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(MemberBookingView, self).get_context_data(**kwargs)
        context['held_dates'] = HeldBookings.objects.all()
        return context


def unit_booked_date(request):
    unit_id = request.GET.get('unit')
    booked_date = HeldBookings.objects.filter(unit_id=unit_id)
    return render(request, 'backend/bookings/ajax_load_booked_dates.html', {'booked_dates': booked_date})


def load_ajax_cat(request):
    facility_id = request.GET.get('facility')
    category = Category.objects.filter(facility_id=facility_id)
    return render(request, 'backend/bookings/ajax_load_cate.html', {'category': category})


def load_ajax_unit(request):
    category_id = request.GET.get('category')
    unit = Unit.objects.filter(category_id=category_id)
    return render(request, 'backend/bookings/ajax_load_unit.html', {'unit': unit})


class AllBookings(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Bookings
    template_name = 'backend/bookings/all_bookings.html'
    raise_exception = True
    permission_required = 'bookings.view_all_bookings'

    def get_context_data(self, **kwargs):
        context = super(AllBookings, self).get_context_data(**kwargs)
        context['booking_list'] = Bookings.objects.all().order_by('-id')

        return context


def discount_booking(request, booking_id):
    try:
        amount = int(request.POST['amount'])
        if amount > 0:
            booking = Bookings.objects.get(id=booking_id)
            booking.discount = amount
            booking.save()
            messages.success(request, 'Discount applied to booking')
        else:
            messages.error(request, 'Discount amount cannot be negative or zero')
    except Bookings.DoesNotExist:
        messages.error(request, 'Booking does not exist')

    return redirect('all_bookings')


#  individual booking in member login
class MyBookings(LoginRequiredMixin, ListView):
    model = Bookings
    template_name = 'backend/bookings/all_bookings.html'
    # raise_exception = True

    # def test_func(self):
    #     member = Member.objects.get(username=self.request.user.username).member_id
    #     my_bookings = Bookings.objects.filter(member_id=self.kwargs['member_id'])
    #     for booking in my_bookings:
    #         if booking.member_id == member:
    #             return True
    #         else:
    #             return False

    def get_context_data(self, **kwargs):
        context = super(MyBookings, self).get_context_data(**kwargs)
        context['booking_list'] = Bookings.objects.filter(member_id=self.kwargs['member_id']).order_by('-id')
        return context


class EditBookings(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Bookings
    template_name = 'backend/bookings/new_bookings.html'
    form_class = MemberBookingForm
    pk_url_kwarg = 'booking_id'
    success_url = reverse_lazy('all_bookings')
    raise_exception = True
    permission_required = 'bookings.change_bookings'

    def form_valid(self, form):
        with transaction.atomic():
            unit = self.request.POST.get('unit')
            form.instance.category_id = Unit.objects.get(id=unit).category_id
            form.save()
            messages.success(self.request, 'Your bookings has been edited Successfully')
        return super(EditBookings, self).form_valid(form)


def delete_booking(request, booking_id):
    with transaction.atomic():
        try:
            get_booking = Bookings.objects.get(id=booking_id)

            log = ActivityLog.objects.create(
                log_text='%s deleted a booking of %s with ID #%s' % (request.user.username, get_booking.member,
                                                                     get_booking.id),
                user_id=request.user.id
            )
            log.save()
            user_type = UserType.objects.get(user_id=request.user.id)
            if user_type.account_type == 1:
                get_member = Member.objects.get(username=request.user.username)
                if get_booking.member_id == get_member.member_id:
                    if get_booking.is_secured is False:
                        for item in HeldBookings.objects.filter(booking_id=booking_id):
                            item.delete()
                        get_booking.delete()

                        messages.success(request, 'You have successfully deleted a booking')

                    else:
                        messages.warning(request, 'Error!. This booking cannot be deleted. It is already secured')
                else:
                    messages.error(request, 'Systematic Error. You are trying to delete a booking that isn\'t yours')
            else:
                if get_booking.is_secured is False:
                    for item in HeldBookings.objects.filter(booking_id=booking_id):
                        item.delete()
                    get_booking.delete()

                    messages.success(request, 'You have successfully deleted a booking')

                else:
                    messages.warning(request, 'Error!. This booking cannot be deleted. It is already secured')

        except Bookings.DoesNotExist:
            messages.error(request, 'Systematic Error. No booking exist with that ID')

    return redirect('all_bookings')


class SelectBank(TemplateView):
    template_name = 'backend/bookings/select_bank.html'

    def get_context_data(self, **kwargs):
        context = super(SelectBank, self).get_context_data(**kwargs)
        context['bank_account'] = BankAcc.objects.all()
        return context

    def get_success_url(self):
        return reverse_lazy('secure_booking', self.kwargs['booking_id'])


@permission_required(perm='bookings.approve_bookings', raise_exception=True)
def approve_booking(request, booking_id):
    get_booking = Bookings.objects.get(id=booking_id)
    get_staff = StaffModel.objects.get(user_id=request.user.id)

    with transaction.atomic():
        if get_booking.is_member:
            try:
                wallet_balance = WalletBalance.objects.get(member_id=get_booking.member_id)
                if wallet_balance.amount - get_booking.payable < 0:
                    messages.error(request, 'Error!!! Insufficient Balance')
                else:
                    wallet_balance.amount -= get_booking.payable
                    wallet_balance.save()
                    get_booking.is_secured = True
                    get_booking.save()
                    debit = Debit.objects.create(
                        member_id=get_booking.member_id,
                        amount=get_booking.payable,
                        staff_id=get_staff.id,
                        trans_id=get_booking.id,
                        remarks='Debit transaction for a booking with ID #%s' % get_booking.id

                    )
                    debit.save()

                    log = ActivityLog.objects.create(
                        log_text='%s approve booking of %s with ID of %s' % (request.user.username, get_booking.member,
                                                                             get_booking.id),
                        user_id=request.user.id

                    )
                    log.save()

                    post_credit_post_sagamy(
                        request,
                        facility_id=get_booking.facility_id,
                        ref_id=booking_id,
                        guest_name=None,
                        guest_phone=None,
                        amount=get_booking.payable,
                        pay_mode=3,
                        account=str(HubGL.objects.get(category_id=get_booking.category_id).acc_no),
                        member_id=None,
                        trans_type='booking of %s for booking ID %s' % (get_booking.payable, booking_id),
                        debit_account='2121'
                    )
                    messages.success(request, 'Member Booking secured!')

            except WalletBalance.DoesNotExist:
                messages.error(request, 'Systematic Error!. Member has not been activated ')

            return redirect('all_bookings')
        else:
            get_booking.is_secured = True
            get_booking.save()
            log = TransactionLog.objects.create(
                trans_id=get_booking.id,
                trans_type=2,
                log='%s secured a booking with ID #%s' % (get_staff.first_name + ' ' + get_staff.last_name,
                                                          get_booking.id),
                facility_id=get_staff.facility_id,
                staff_id=get_staff.id
            )
            log.save()

            bank_account = BankAcc.objects.get(id=request.POST['bank']).account_no

            post_credit_post_sagamy(
                request,
                facility_id=get_booking.facility_id,
                ref_id=booking_id,
                guest_name=get_booking.guest_name,
                guest_phone=get_booking.guest_phone,
                amount=get_booking.payable,
                pay_mode=3,
                account=str(HubGL.objects.get(category_id=get_booking.category_id).acc_no),
                member_id=0,
                trans_type='makes of booking of %s' % get_booking.payable,
                debit_account=str(bank_account)
            )

            message = render_to_string('emails/booking_payment_received.html', {
                'user': get_booking.guest_name,
                'booked_facility': get_booking.facility,
                'booked_category': get_booking.category,
                'booked_unit': get_booking.unit,
                'book_from': get_booking.book_from,
                'book_to': get_booking.book_to,
                'booking_id': booking_id,
            })
            mail_subject = 'Enterprise Hubs Booking Payment Received'
            to_email = get_booking.guest_email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()

            messages.success(request, 'Guest booking has been secured')
            return redirect('all_bookings')







