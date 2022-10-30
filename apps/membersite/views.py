# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from .models import MainSite, Portfolio
from django.contrib import messages
from .forms import WebSpaceForm, EditWebSpaceForm, PortfolioForm
from ..members.models import Member
from django.db import transaction
from django.shortcuts import redirect
# from django.core.exceptions import ValidationError
from ..account.models import UserType
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.


class BuildMyWebSpace(LoginRequiredMixin, CreateView):
    model = MainSite
    template_name = 'backend/web_space/build_web_space.html'
    form_class = WebSpaceForm

    def get_success_url(self):
        member_id = Member.objects.get(username=self.request.user.username).member_id
        return reverse_lazy('view_my_web_space', args=[member_id])

    def form_valid(self, form):
        try:
            MainSite.objects.get(user_id=self.request.user.id)
            raise PermissionDenied
        except MainSite.DoesNotExist:
            member_id = Member.objects.get(username=self.request.user.username).member_id
            form.instance.member_id = member_id
            form.instance.user_id = self.request.user.id
            messages.success(self.request, 'Web Space Created Successfully')
        return super(BuildMyWebSpace, self).form_valid(form)


class UpdateMyWebSpace(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = MainSite
    template_name = 'backend/web_space/build_web_space.html'
    form_class = WebSpaceForm
    pk_url_kwarg = 'web_space_id'
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

    def get_success_url(self):
        return reverse_lazy('view_my_web_space', args=[self.object.member_id])

    def form_valid(self, form):
        messages.success(self.request, 'Web Space Updated Successfully')
        return super(UpdateMyWebSpace, self).form_valid(form)


class CreatePortfolio(LoginRequiredMixin, CreateView):
    model = Portfolio
    template_name = 'backend/web_space/create_portfolio.html'
    success_url = reverse_lazy('build_web_space')
    form_class = WebSpaceForm

    def get_success_url(self):
        member_id = Member.objects.get(username=self.request.user.username).member_id
        return reverse_lazy('view_my_web_space', args=[member_id])


class ViewMyWebSpace(LoginRequiredMixin, CreateView):
    template_name = 'backend/web_space/web_space.html'
    pk_url_kwarg = 'member_id'
    form_class = PortfolioForm
    model = Portfolio

    def get_success_url(self):
        user_type = UserType.objects.get(user_id=self.request.user.id)
        if user_type.account_type == 2:
            member_id = self.kwargs['member_id']
        else:
            member_id = Member.objects.get(username=self.request.user.username).member_id
        return reverse_lazy('view_my_web_space', args=[member_id])

    def get_context_data(self, **kwargs):
        context = super(ViewMyWebSpace, self).get_context_data(**kwargs)

        user_type = UserType.objects.get(user_id=self.request.user.id)
        if user_type.account_type == 2:
            member_id = self.kwargs['member_id']
        else:
            member_id = Member.objects.get(username=self.request.user.username).member_id
        try:
            context['web_space'] = MainSite.objects.get(member_id=member_id)
        except MainSite.DoesNotExist:
            context['web_space'] = None
        try:
            context['portfolio'] = Portfolio.objects.filter(member_id=member_id)
            context['portfolio_count'] = Portfolio.objects.filter(member_id=member_id).count()
        except Portfolio.DoesNotExist:
            context['portfolio'] = None
        return context

    def form_valid(self, form):
        with transaction.atomic():
            user_type = UserType.objects.get(user_id=self.request.user.id)
            if user_type.account_type == 2:
                member_id = self.kwargs['member_id']
            else:
                member_id = Member.objects.get(username=self.request.user.username).member_id
            form.instance.member_id = member_id
            messages.success(self.request, 'Item added to your portfolio successfully')
        return super(ViewMyWebSpace, self).form_valid(form)


@login_required()
def delete_portfolio(request, portfolio_id):
    get_portfolio = Portfolio.objects.get(id=portfolio_id)
    get_portfolio.delete()
    user_type = UserType.objects.get(user_id=self.request.user.id)
    if user_type.account_type == 2:
        member_id = self.kwargs['member_id']
    else:
        member_id = Member.objects.get(username=self.request.user.username).member_id
    messages.success(request, 'Item deleted successfully')

    return redirect('view_my_web_space', member_id)


@login_required
def request_setup(request, member_id):
    get_member = Member.objects.get(member_id=member_id)

    message = render_to_string('emails/portal_design.html', {
        'name': get_member.first_name + ' ' + get_member.last_name,
        'id': get_member.member_id,
        'phone': get_member.phone,
    })
    mail_subject = 'Enterprise Portal Request Design'
    to_email = 'info@enterprisehubs.com'
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.content_subtype = 'html'
    send_email.send()

    messages.success(request, 'Thank you, we have received your request. You will be contacted with more information')

    return redirect('view_my_web_space', member_id)

