# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import requests
from django.conf import settings
from django.contrib.sites import requests
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, UpdateView, DetailView, FormView, TemplateView
from .forms import MemberShipRegistrationForm, MemberShipUpdateForm, ChangePackageType, CreditSelfForm, \
    MemberUpdateSelfForm, ResourceCenterForm
from django.shortcuts import redirect
from django.contrib import messages
from .models import Member, PaymentResources, MembershipType, CentralDatabase
import random
from ..billables.models import WalletBalance, Debit
from django.contrib.auth.models import User
from ..helpers.services import GenerateSheet, generate_sheet
from ..staff.models import StaffModel, ActivityLog
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
import datetime
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import permission_required, login_required
from ..bookings.models import Bookings
from ..billables.models import Credit
from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.models import Group
from ..account.models import UserType
from ..membersite.models import MainSite
from ..onboarding.models import FrontDesk

# Create your views here.


class NewMember(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'backend/members/new_member.html'
    form_class = MemberShipRegistrationForm
    success_url = reverse_lazy('new_member')
    member_id = random.randrange(1, 1234567890, 5)
    password = User.objects.make_random_password()
    raise_exception = True

    def test_func(self):
        user_type = UserType.objects.get(user_id=self.request.user.id)
        if user_type.account_type == 2:
            return True
        else:
            return False

    def form_valid(self, form):
        with transaction.atomic():
            try:
                form.instance.member_id = self.member_id
            except:
                form.instance.member_id = random.randrange(1, 9876543210, 5)
            form.save()
            create_user = User.objects.create_user(
                username=form.instance.username,
                password=self.password,
                first_name=form.instance.first_name,
                last_name=form.instance.last_name,
                email=form.instance.email,
                is_active=False,
            )
            create_user.save()

            group, created = Group.objects.get_or_create(name='member')
            group.user_set.add(create_user.id)

            create_log = ActivityLog.objects.create(
                log_text='%s created a new member (%s)' % (self.request.user.username, form.instance.username),
                user_id=self.request.user.id
            )
            create_log.save()

            create_account_type = UserType.objects.create(account_type=1, user_id=create_user.id)
            create_account_type.save()

            message = render_to_string('emails/account_activation_email.html', {
                'user': form.instance.username,
                'domain': get_current_site(self.request).domain,
                'uid': urlsafe_base64_encode(force_bytes(create_user.id)),
                'token': account_activation_token.make_token(create_user),
                'password': self.password
            })
            mail_subject = 'Welcome to Enterprise Hubs. Please activate you email'
            to_email = form.instance.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()

            messages.success(self.request, 'New Member Created Successfully')
        return super(NewMember, self).form_valid(form)


def manual_membership_activation(request, member_id):
    member = Member.objects.get(member_id=member_id)
    staff = StaffModel.objects.get(username=request.user.username)
    amount = request.POST['amount']
    expiry = request.POST['expiry_date']
    pay_mode = request.POST['pay_mode']
    trans_id = random.randrange(1, 987654321, 3)
    with transaction.atomic():
        credit = Credit.objects.create(
            facility_id=staff.facility_id,
            trans_id=trans_id,
            member_id=member_id,
            amount=amount,
            staff_id=staff.id,
            payment_mode=pay_mode,
            comment="%s was credited for membership registration" % amount,
            sagamy_trans_id=0,
        )
        credit.save()
        debit = Debit.objects.create(
            trans_id=trans_id,
            member_id=member_id,
            amount=amount,
            staff_id=staff.id,
            remarks="%s was debited for membership registration" % amount
        )
        debit.save()
        activity = ActivityLog.objects.create(
            log_text="%s manually override membership for %s for %s, expiring in %s" %(staff.user.get_full_name(),
                                                                                      member.first_name, amount, expiry),
            user=request.user
        )
        activity.save()

        today = datetime.date.today()
        member.approve_date = today
        member.last_pay_date = today
        member.expire_date = expiry
        member.is_active = True
        member.is_activated = True
        member.save()

        messages.success(request, 'You have successfully activated this user')

    return redirect("member_details",member_id)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    get_member = Member.objects.get(username=user.username)
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        get_member.validated = True
        get_member.save()
        login(request, user)  # Commented because i don't want to automatically login member after mail validation
        messages.success(request, 'You email has been activated. You will be notified when your account has '
                                  'been activated by admin, Please make payment for your membership type.')

        message = render_to_string('emails/email_activate_complete.html', {
            'user': (user.first_name + ' ' + user.last_name),
        })
        mail_subject = 'Enterprise Hubs, One more step ..'
        to_email = user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.content_subtype = 'html'
        send_email.send()

        return redirect('member_account', get_member.member_id)
    else:
        messages.warning(request, 'Error. Link expired')
        return redirect('login')


class UpdateMember(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Member
    template_name = 'backend/members/new_member.html'
    form_class = MemberShipUpdateForm
    pk_url_kwarg = 'member_id'
    success_url = reverse_lazy('all_members')
    raise_exception = True

    def test_func(self):
        user_type = UserType.objects.get(user_id=self.request.user.id)
        if user_type.account_type == 2:
            return True
        else:
            return False

    def form_valid(self, form):
        create_log = ActivityLog.objects.create(
            log_text='%s updated a member account (%s)' % (self.request.user.username, self.object.username),
            user_id=self.request.user.id
        )
        create_log.save()
        messages.success(self.request, 'Action Successfully')
        return super(UpdateMember, self).form_valid(form)


class MemberDetails(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Member
    template_name = 'backend/members/member_details.html'
    pk_url_kwarg = 'member_id'
    raise_exception = True

    def test_func(self):
        user_type = UserType.objects.get(user_id=self.request.user.id)
        if user_type.account_type == 2:
            return True
        else:
            self.object = self.get_object()  # test_function cannot access object directly, hence we use get_object
            check_member = Member.objects.get(username=self.request.user.username)
            if self.object.member_id == check_member.member_id:
                return True
            else:
                return False

    def get_context_data(self, **kwargs):
        context = super(MemberDetails, self).get_context_data(**kwargs)
        total_credit = Credit.objects.filter(member_id=self.object.member_id, is_reversed=False)
        sum_credit = sum(total_credit.values_list('amount', flat=True))
        context['total_credit'] = sum_credit
        try:
            context['wallet_balance'] = WalletBalance.objects.get(member_id=self.object.member_id).amount
        except WalletBalance.DoesNotExist:
            context['wallet_balance'] = 0
        booking = Bookings.objects.filter(member_id=self.object.member_id)
        context['bookings'] = booking.count()
        context['all_bookings'] = booking.order_by('-id')
        context['recent_credit'] = total_credit.order_by('-date')

        context['recent_debit'] = Debit.objects.filter(member_id=self.object.member_id).order_by('-date')

        return context


class UpdateMemberSelf(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Member
    template_name = 'backend/staff/update_staff_self.html'
    form_class = MemberUpdateSelfForm
    pk_url_kwarg = 'member_id'
    raise_exception = True

    def test_func(self):
        self.object = self.get_object()  # test_function cannot access object directly, hence we use get_object
        check_member = Member.objects.get(username=self.request.user.username)
        if self.object.member_id == check_member.member_id:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse_lazy('member_details', args=[self.object.member_id])

    def get_context_data(self, **kwargs):
        context = super(UpdateMemberSelf, self).get_context_data(**kwargs)
        # Passing Member object as staff because i used staff_update_template and the param is staff.
        context['staff'] = User.objects.get(username=self.request.user.username)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'You successfully updated your profile')
        return super(UpdateMemberSelf, self).form_valid(form)


class VisitingCustomerList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = FrontDesk
    template_name = 'backend/members/visiting_clients_list.html'
    raise_exception = True

    def get_queryset(self):
        if 'filter_from' in self.request.GET and 'filter_to' in self.request.GET:
            filter_from = self.request.GET.get('filter_from')
            filter_to = self.request.GET.get('filter_to')
        else:
            filter_from = datetime.date.today() - datetime.timedelta(30)
            filter_to = datetime.date.today()
        query = FrontDesk.objects.filter(
            date__date__lte=filter_to,
            date__date__gte=filter_from
        ).order_by('-date')
        return query

    def test_func(self):
        user_type = UserType.objects.get(user_id=self.request.user.id)
        if user_type.account_type == 2:
            return True
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super(VisitingCustomerList, self).get_context_data(**kwargs)
        if 'filter_from' in self.request.GET and 'filter_to' in self.request.GET:
            context['filter_from'] = datetime.datetime.strptime(self.request.GET.get('filter_from'), '%Y-%m-%d')
            context['filter_to'] = datetime.datetime.strptime(self.request.GET.get('filter_to'), '%Y-%m-%d')
        else:
            context['filter_from'] = datetime.date.today() - datetime.timedelta(30)
            context['filter_to'] = datetime.date.today()
        return context


class MemberList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Member
    template_name = 'backend/members/all_members.html'
    raise_exception = True

    def test_func(self):
        user_type = UserType.objects.get(user_id=self.request.user.id)
        if user_type.account_type == 2:
            return True
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super(MemberList, self).get_context_data(**kwargs)
        context['member_list'] = Member.objects.all().order_by('-date_joined')

        def check_expiry_date_in_past():
            try:
                for member in Member.objects.filter(validated=True):
                    if member.approve_date:
                        if datetime.date.today() > member.expire_date:
                            return True
                        else:
                            return False

            except TypeError:
                pass
        context['expiry_in_past'] = check_expiry_date_in_past()

        return context


def generate_report_sheet(request, from_date, to_date, sheet_type):
    # GenerateSheet(from_date=from_date, to_date=to_date, sheet_type=sheet_type).start()
    if sheet_type == 'visitors':
        return generate_sheet(from_date=from_date, to_date=to_date, sheet_type=sheet_type, loc='download')
    else:
        return generate_sheet(from_date=from_date, to_date=to_date, sheet_type=sheet_type, loc='download')


@login_required()
@permission_required(perm='members.activate_member_account', raise_exception=True)
def activate_member_account(request, member_id):

    try:
        with transaction.atomic():
            wallet = WalletBalance.objects.get(member_id=member_id)
            member = Member.objects.get(member_id=member_id)

            if member.validated is True:

                if int(wallet.amount) - int(member.type.amount) < 0:
                    messages.error(request, 'Error!!!. Insufficient Fund')
                else:
                    wallet.amount -= member.type.amount
                    wallet.save()
                    staff = StaffModel.objects.get(username=request.user.username)

                    create_log = ActivityLog.objects.create(
                        log_text='%s activated a member account (%s)' % (request.user.username, member.username),
                        user_id=request.user.id
                    )
                    create_log.save()

                    member.approve_date = datetime.date.today()
                    member.expire_date = datetime.date.today() + datetime.timedelta(days=member.type.validity)
                    member.is_active = True
                    member.is_activated = True
                    member.save()

                    user = User.objects.get(username=member.username)
                    user.is_active = True
                    user.save()

                    debit = Debit.objects.create(
                        member_id=member_id,
                        amount=member.type.amount,
                        staff_id=staff.id,
                        trans_id=random.randrange(1, 1234567890, 5)

                    )
                    debit.save()

                    # post_credit_post_sagamy(
                    #     request,
                    #     facility_id=None,
                    #     ref_id=debit.trans_id,
                    #     guest_name=None,
                    #     guest_phone=None,
                    #     member_id=member_id,
                    #     amount=member.type.amount,
                    #     pay_mode=3,
                    #     account='3127',
                    #     trans_type='paid for membership account renewal with transaction ID #%s' % debit.trans_id,
                    #     debit_account='1110',
                    # )
                    site = MainSite.objects.create(
                        member_id=member_id,
                        user_id=user.id
                    )
                    # site.save()

                    message = render_to_string('emails/email_activate_complete.html', {
                        'user': (user.first_name + ' ' + user.last_name),
                    })
                    mail_subject = 'Enterprise Hubs, Congrats Account Activated'
                    to_email = user.email
                    send_email = EmailMessage(mail_subject, message, to=[to_email])
                    send_email.content_subtype = 'html'
                    send_email.send()
                    messages.success(request, 'Member has been activated successfully')
            else:
                messages.warning(request, 'Error: Member has email has not been validated')

            return redirect('all_members')

    except WalletBalance.DoesNotExist:
        messages.error(request, 'Please credit Member First')
        return redirect('all_members')


@login_required()
@permission_required(perm='members.deactivate_member', raise_exception=True)
def deactivate_member(request, member_id):
    member = Member.objects.get(member_id=member_id)
    member.is_active = False
    member.save()
    user = User.objects.get(username=member.username)
    user.is_active = False

    create_log = ActivityLog.objects.create(
        log_text='%s deactivated a member account (%s)' % (request.user.username, member.username),
        user_id=request.user.id
    )
    create_log.save()

    user.save()
    messages.success(request, 'Member has been Blocked')

    return redirect('all_members')


@login_required()
@permission_required(perm='members.activate_member', raise_exception=True)
def activate_member(request, member_id):
    member = Member.objects.get(member_id=member_id)
    member.is_active = True
    member.save()
    user = User.objects.get(username=member.username)
    user.is_active = True
    user.save()

    site = MainSite.objects.get_or_create(
        member_id=member_id,
        user_id=user.id
    )
    # site.save()

    # create_log = ActivityLog.objects.create(
    #     log_text='%s re-activated a member account (%s)' % (request.user.username, member.username),
    #     user_id=request.user.id
    # )
    # create_log.save()

    messages.success(request, 'Member has been re-activated')

    return redirect('all_members')


@login_required()
@permission_required(perm='members.delete_member', raise_exception=True)
def delete_member(request, member_id):
    member = Member.objects.get(member_id=member_id)
    if not Credit.objects.filter(member_id=member_id).exists():

        create_log = ActivityLog.objects.create(
            log_text='%s deleted a member account (%s)' % (request.user.id, member.username),
            user_id=request.user.id
        )
        create_log.save()

        member.delete()
        user = User.objects.get(username=member.username)
        user.delete()
        messages.success(request, 'Member has been deleted')
    else:
        messages.error(request, 'Error!. Cannot delete this member, please deactivate instead')
    return redirect('all_members')


class MemberAccount(LoginRequiredMixin, UpdateView):
    model = Member
    template_name = 'backend/members/member_account_renewal.html'
    pk_url_kwarg = 'member_id'
    form_class = ChangePackageType

    def get_success_url(self):
        member_id = Member.objects.get(username=self.request.user.username).member_id
        return reverse_lazy('member_account', args=[member_id])

    def get_context_data(self, **kwargs):

        context = super(MemberAccount, self).get_context_data(**kwargs)
        context['member'] = Member.objects.get(member_id=self.object.member_id)
        return context


class CreditSelf(LoginRequiredMixin, FormView):
    template_name = 'backend/wallet/credit_wallet.html'
    form_class = CreditSelfForm
    success_url = reverse_lazy('credit_member')
    raise_exception = True

    def get_success_url(self):
        member_id = Member.objects.get(username=self.request.user.username).member_id
        amount = self.request.POST.get('amount')
        return reverse_lazy('payment_resources', args=[member_id, 'credit_self', amount])

    def form_valid(self, form):
        # Todo Email Notification of success credit
        return super(CreditSelf, self).form_valid(form)


def payment_resources(request, member_id, t_type, amount):
    ref_id = random.randrange(0, 9876543210, 4)
    PaymentResources.objects.create(
        status=False,
        amount=amount,
        ref_id=ref_id,
        member_id=member_id
    )
    get_member = Member.objects.get(member_id=member_id)

    return render(request, 'backend/members/member_account_renewal.html', {'member': get_member, 'ref_id': ref_id,
                                                                           'amount': amount, 't_type': t_type})


def check_type_validity(member_id):
    try:
        member = Member.objects.get(member_id=member_id)
        if member.upgrade_type:
            type_validity = MembershipType.objects.get(id=member.upgrade_type_id).validity
            return type_validity
        else:
            type_validity = MembershipType.objects.get(id=member.type_id).validity
            return type_validity
    except Member.DoesNotExist:
        pass


def post_credit_post_sagamy(request, facility_id, ref_id, guest_name, guest_phone, amount, pay_mode, account, member_id,
                            trans_type, debit_account):
    print (ref_id)
    if member_id is None:
        customer = 'A member'

    elif member_id != 0:
        get_member = Member.objects.get(member_id=member_id)
        customer = get_member.first_name + ' ' + get_member.last_name
        credit_log = Credit.objects.create(
            facility_id=facility_id,
            trans_id=ref_id,
            member_id=member_id,
            amount=amount,
            payment_mode=pay_mode,
            comment='%s %s' % (customer, trans_type),
            sagamy_trans_id=0

        )
        credit_log.save()

    elif member_id == 0:
        customer = guest_name
        credit_log = Credit.objects.create(
            facility_id=facility_id,
            trans_id=ref_id,
            guest_name=guest_name,
            guest_phone=guest_phone,
            amount=amount,
            payment_mode=pay_mode,
            comment='%s %s' % (customer, trans_type),
            sagamy_trans_id=0

        )
        credit_log.save()

    # API to connect to Sagamy Accounting Software to POST transactions
    # payload = {'Username': 'test', 'Password': 'test123', 'BranchID': '3', 'AppMode': 'API'}
    # response = requests.post('http://23.101.73.29:5010/pedestal/sagamyonlinegateway/API/Login/', data=payload)
    # serialize_json = response.json()
    # session_id = serialize_json['Payload']['SessionId']
    # headers = {"Content-Type": "application/json", "Authorization": "Sagamy:" + session_id}
    # parameters = [
    #     {
    #         'AccountNumber': account,
    #         'GlEntryType': '1',
    #         'Amount': amount,
    #         'Comments': '%s makes a %s' % (customer, trans_type),
    #         'Fee': '0.00',
    #         'Commit': 'false'
    #     },
    #     {
    #         'AccountNumber': debit_account,
    #         'GlEntryType': '2',
    #         'Amount': amount,
    #         'Comments': '%s makes a %s' % (customer, trans_type),
    #         'Fee': '0.00',
    #         'Commit': 'false'
    #     },
    # ]
    # post_data = requests.post('http://23.101.73.29:5010/pedestal/sagamyonlinegateway/api/electronicFundsTransfer/batch/', json=parameters,
    #                           headers=headers)
    # get_success_message = post_data.json()
    #
    # if member_id is not None:
    #     try:
    #         credit_log.sagamy_trans_id = get_success_message['Payload']['BatchId']  # batchId response from Sagamy
    #     except TypeError:
    #         try:
    #             raise SystemError(get_success_message['Payload']['ErrorDetails'])
    #         except TypeError:
    #             raise SystemError(get_success_message['ErrorDetails'])


def verify_payment(request, member_id, ref_id, t_type):
    headers = {"Content-Type": 'application/json', "Authorization": "Bearer " + settings.PAYSTACK_KEY}
    response = requests.get('https://api.paystack.co/transaction/verify/' + ref_id, headers=headers)
    pay_stack = response.json()
    status = pay_stack['status']
    pay_stack_message = pay_stack['message']

    with transaction.atomic():
        if status is True:
            member = Member.objects.get(member_id=member_id)
            trans_id = random.randrange(1, 987654321, 4)

            if t_type == 'activate_fee':
                if member.upgrade_type:
                    amount = member.upgrade_type.amount
                else:
                    amount = member.type.amount

                try:
                    WalletBalance.objects.get(member_id=member_id)
                except WalletBalance.DoesNotExist:
                    create_wallet = WalletBalance.objects.create(member_id=member_id, amount=amount)
                    create_wallet.save()

                today = datetime.date.today()

                if member.expire_date is None:
                    member.last_pay_date = today
                    member.expire_date = today + datetime.timedelta(days=check_type_validity(member_id))
                else:
                    member.last_pay_date = today
                    member.expire_date += datetime.timedelta(days=check_type_validity(member_id))

                member.last_pay_date = datetime.date.today()

                message = render_to_string('emails/new_member_payment_received.html', {
                    'user': (member.first_name + ' ' + member.last_name),
                    'amount': amount,
                    'type': 'member'
                })
                message2 = render_to_string('emails/new_member_payment_received.html', {
                    'type': 'staff',
                    'member': (member.first_name + ' ' + member.last_name),
                    'member_id': member.member_id
                })

                hq_email = 'info@enterprisehubs.com'
                hq_subject = 'New member payment received'
                mail_subject = 'Enterprise Hubs, Payment Received'
                to_email = member.email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_hq_mail = EmailMessage(hq_subject, message2, hq_email)
                send_hq_mail.content_subtype = 'html'
                send_email.content_subtype = 'html'
                send_hq_mail.send()
                send_email.send()
                messages.success(request, 'Your payment has been received. '
                                          'We are currently reviewing your registration. '
                                          'You will be notified once we activate your account.')

                post_credit_post_sagamy(
                    request,
                    facility_id=None,
                    ref_id=trans_id,
                    guest_name=None,
                    guest_phone=None,
                    member_id=member_id,
                    amount=amount,
                    pay_mode=3,
                    account='3127',
                    trans_type='payment for membership activation fee with transaction ID #%s' % trans_id,
                    debit_account='1110',
                )

            if t_type == 'account_renewal':
                today = datetime.date.today()

                if member.expire_date is None:
                    member.last_pay_date = today
                    member.expire_date = today + datetime.timedelta(days=check_type_validity(member_id))
                else:
                    member.last_pay_date = today
                    member.expire_date += datetime.timedelta(days=check_type_validity(member_id))

                if member.upgrade_type:
                    member.type = member.upgrade_type
                    amount = member.upgrade_type.amount
                else:
                    amount = member.type.amount
                member.is_active = True
                member.save()

                post_credit_post_sagamy(
                    request,
                    facility_id=None,
                    ref_id=trans_id,
                    guest_name=None,
                    guest_phone=None,
                    member_id=member_id,
                    amount=amount,
                    pay_mode=3,
                    account='3103',
                    trans_type='paid for membership activation fee with transaction ID #%s' % trans_id
                )

                debit_create = Debit.objects.create(
                    trans_id=ref_id,
                    member_id=member_id,
                    amount=amount,
                    remarks='%s got a debit transaction for account renewal' % member.first_name + ' ' + member.last_name

                )
                debit_create.save()

                message = render_to_string('emails/new_member_payment_received.html', {
                    'type': 'account_renewal',
                    'member': (member.first_name + ' ' + member.last_name),
                    'account': member.type,
                    'amount': amount,
                    'next_p_date': member.expire_date,

                })

                mail_subject = 'Enterprise Hubs, Account renewed successfully'
                to_email = member.email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.content_subtype = 'html'
                send_email.send()

                messages.success(request, 'Your payment has been received.')

            if t_type == 'credit_self':
                amount = PaymentResources.objects.get(ref_id=ref_id).amount

                post_credit_post_sagamy(
                    request,
                    facility_id=None,
                    ref_id=trans_id,
                    guest_phone=None,
                    guest_name=None,
                    member_id=member_id,
                    amount=amount,
                    pay_mode=3,
                    account='2121',
                    trans_type='credit self on the portal with transaction ID #%s' % trans_id,
                    debit_account='1110'
                )

                wallet = WalletBalance.objects.get(member_id=member_id)
                wallet.amount += amount
                wallet.save()

                message = render_to_string('emails/new_member_payment_received.html', {
                    'type': 'credit_self',
                    'member': (member.first_name + ' ' + member.last_name),
                    'amount': amount,
                    'wallet_balance': wallet.amount,

                })

                mail_subject = 'Enterprise Hubs, credit transaction'
                to_email = member.email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.content_subtype = 'html'
                send_email.send()

                messages.success(request, 'Your payment has been received.')

            payment_resource = PaymentResources.objects.get(ref_id=ref_id)
            payment_resource.status = True
            payment_resource.save()

        else:
            messages.error(request, 'Error!!!, Payment unsuccessful with error message: %s' % pay_stack_message)

        if t_type == 'activate_fee':
            return redirect('member_account', member_id)

        if t_type == 'account_renewal':
            return redirect('member_account', member_id)

        elif t_type == 'credit_self':
            return redirect('credit_self')


class CentralDB(CreateView):
    template_name = 'backend/members/central_db_upload.html'
    form_class = ResourceCenterForm

    def get_success_url(self):
        member_id = Member.objects.get(username=self.request.user.username).member_id
        return reverse('central_database_list', kwargs={'member_id': member_id})

    def form_valid(self, form):
        member_id = Member.objects.get(username=self.request.user.username).member_id
        form.instance.owned_by_id = member_id
        form.save()
        messages.success(self.request, 'File added to your central database successfully')
        return super(CentralDB, self).form_valid(form)


class CentralDBList(TemplateView):
    template_name = 'backend/members/central_db_list.html'

    def get_context_data(self, **kwargs):
        context = super(CentralDBList, self).get_context_data(**kwargs)
        try:
            member_id = self.kwargs['member_id']
            context['file_list'] = CentralDatabase.objects.filter(owned_by=member_id)
        except Member.DoesNotExist:
            pass
        return context


def central_db_delete(request, item_id):
    member_id = Member.objects.get(username=request.user.username).member_id
    get_item = CentralDatabase.objects.get(id=item_id)
    get_item.delete()
    messages.success(request, 'Item was deleted from Database Successfully')
    return redirect('central_database_list', member_id)


