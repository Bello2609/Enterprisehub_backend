# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, FormView
from .models import Credit
from .forms import CreditMemberForm
from django.contrib import messages
from .models import TransactionLog, WalletBalance
from django.db import transaction
from ..staff.models import StaffModel, ActivityLog
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import random
from ..account.models import BankAcc
from ..members.views import post_credit_post_sagamy
from datetime import datetime
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.shortcuts import redirect

# Create your views here.


class CreditMember(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    template_name = 'backend/wallet/credit_wallet.html'
    form_class = CreditMemberForm
    success_url = reverse_lazy('credit_member')
    raise_exception = True
    permission_required = 'billables.credit_member'

    def get_context_data(self, **kwargs):
        context = super(CreditMember, self).get_context_data(**kwargs)
        context['bank_account'] = BankAcc.objects.all()
        return context

    def form_valid(self, form):
        with transaction.atomic():
            trans_id = random.randrange(1, 987654321, 4)
            username = self.request.user.username
            get_staff = StaffModel.objects.get(username=username)
            form.instance.staff_id = get_staff.id
            form.instance.trans_id = trans_id
            form.instance.facility_id = get_staff.facility_id
            form.instance.date = datetime.now()
            form.instance.comment = '%s was credited the sum of %s by %s' % (form.instance.member, form.instance.amount,
                                                                             get_staff.first_name + ' ' +
                                                                             get_staff.last_name)

            if 'bank' in self.request.POST:
                bank_account = str(BankAcc.objects.get(id=self.request.POST['bank']).account_no)
            else:
                bank_account = '3103'

            post_credit_post_sagamy(
                self.request,
                facility_id=get_staff.facility_id,
                ref_id=trans_id,
                guest_name=None,
                guest_phone=None,
                amount=form.instance.amount,
                pay_mode=form.instance.payment_mode,
                account='2121',
                member_id=form.instance.member_id,
                debit_account=bank_account,
                trans_type='was credited the sum of %s by %s with transaction ID #%s' % (form.instance.amount,
                                                                                         get_staff.first_name + ' ' +
                                                                                         get_staff.last_name, trans_id)
            )

            try:
                credit_wallet = WalletBalance.objects.get(member_id=self.request.POST.get('member'))
                credit_wallet.amount += int(self.request.POST.get('amount'))
            except WalletBalance.DoesNotExist:
                credit_wallet = WalletBalance.objects.create(member_id=self.request.POST.get('member'),
                                                             amount=self.request.POST.get('amount'))
            log_it = TransactionLog.objects.create(
                trans_id=form.instance.trans_id,
                trans_type=2,
                log='%s just credited %s with the sum of %s' % (get_staff.first_name + ' ' + get_staff.last_name,
                                                                form.instance.member,
                                                                self.request.POST.get('amount')),
                facility_id=get_staff.facility_id,
                staff_id=get_staff.id
            )
            credit_wallet.save()
            log_it.save()

            message = render_to_string('emails/new_member_payment_received.html', {
                'type': 'credit_self',
                'member': form.instance.member,
                'amount': form.instance.amount,
                'wallet_balance': credit_wallet.amount,

            })

            mail_subject = 'Enterprise Hubs, credit transaction'
            to_email = credit_wallet.member.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()

        messages.success(self.request, 'Your credit transaction was successful')
        return super(CreditMember, self).form_valid(form)


class AllCredit(ListView):
    model = Credit
    template_name = 'backend/wallet/all_credit.html'

    def get_context_data(self, **kwargs):
        context = super(AllCredit, self).get_context_data(**kwargs)
        context['object_list'] = Credit.objects.all().order_by('-date')
        return context


def revert_transaction(request, trans_id):
    with transaction.atomic():
        get_credit = Credit.objects.get(trans_id=trans_id, is_reversed=False)

        # payload = {'Username': 'test', 'Password': 'test123', 'BranchID': '3', 'AppMode': 'API'}
        # response = requests.post('http://23.101.73.29:5010/pedestal/sagamyonlinegateway/API/Login/', data=payload)
        # serialize_json = response.json()
        # session_id = serialize_json['Payload']['SessionId']
        # headers = {"Content-Type": "application/json", "Authorization": "Sagamy:" + session_id}
        # get_credit.save()
        #
        # parameters = {
        #         'BatchId': str(get_credit.sagamy_trans_id),
        #         'ReverseComment': 'Reversal was done on a transaction with ID #%s' % trans_id
        #     }
        #
        # post_data = requests.post(
        #     'http://23.101.73.29:5010/pedestal/sagamyonlinegateway/api/electronicFundsTransfer/reverseBatch/',
        #     json=parameters, headers=headers)
        #
        # post_data = post_data.json()
        # print (post_data)

        log = ActivityLog.objects.create(
            user_id=request.user.id,
            log_text='%s reverted a credit transaction(#%s)' % (request.user.first_name + ' ' +
                                                                request.user.last_name, get_credit.trans_id)
        )
        log.save()
        get_credit.is_reversed = True
        get_credit.save()

        try:
            get_wallet = WalletBalance.objects.get(member_id=get_credit.member_id)
            get_wallet.amount -= get_credit.amount
            get_wallet.save()
            message = render_to_string('emails/new_member_payment_received.html', {
                'type': 'reversed_credit',
                'member': get_wallet.member,
                'amount': get_credit.amount,
                'credit_id': get_credit.trans_id,
                'wallet_balance': get_wallet.amount,

            })

            mail_subject = 'Enterprise Hubs, Reversed transaction'
            to_email = get_wallet.member.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()

        except WalletBalance.DoesNotExist:
            pass

        messages.success(request, 'Transaction has been reversed successfully')

        return redirect('all_credit')



