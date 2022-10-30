# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ..account.models import UserType
from django.shortcuts import redirect, render
from ..staff.models import StaffModel
from ..members.models import Member
from django.http import HttpResponse
from ..bookings.models import Bookings
from ..blog.models import NewPost
from datetime import date
from ..billables.models import Credit
from django.contrib.auth.decorators import login_required
from .forms import ChangePasswordForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
# from django.utils.decorators import method_decorator
# Create your views here.


class ForumView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'backend/forum_file.html'


class Dashboard(LoginRequiredMixin, PermissionRequiredMixin, generic.TemplateView):
    template_name = 'backend/index.html'
    raise_exception = True
    permission_required = 'facility.can_view_dashboard'
    permission_denied_message = 'Sorry, You are not allowed to see this page'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        members = Member.objects.filter(is_active=True)
        context['member_count'] = members.count()
        member_bookings = Bookings.objects.filter(is_member=True)
        context['member_bookings'] = member_bookings.count()
        guest_booking = Bookings.objects.filter(is_member=False)
        context['guest_booking'] = guest_booking.count()
        blog_post = NewPost.objects.all()
        context['blog_post'] = blog_post.count()
        today = date.today()
        credit_year = Credit.objects.filter(date__year=today.year, is_reversed=False)
        credit_year = sum(credit_year.values_list('amount', flat=True))
        context['current_year'] = credit_year
        context['this_year'] = today.year
        credit_month = Credit.objects.filter(date__month=today.month, date__year=today.year, is_reversed=False)
        credit_month = sum(credit_month.values_list('amount', flat=True))
        context['this_month'] = today
        context['current_month'] = credit_month
        context['latest_credit'] = Credit.objects.filter(is_reversed=False).order_by('-date')[:10]

        return context


def login_success(request):
    user_id = request.user.id
    try:
        user_type = UserType.objects.get(user_id=user_id).account_type
        if user_type is 2:
            check_staff = StaffModel.objects.get(user_id=user_id)
            if check_staff.is_oga is True:
                return redirect('dashboard')
            else:
                return redirect('staff_details', check_staff.facility_id, check_staff.id)

        else:
            member = Member.objects.get(username=request.user.username)
            return redirect('member_details', member.member_id)

    except UserType.DoesNotExist:
        return HttpResponse("Error")


@login_required()
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'registration/change_password.html', {'form': form})


def error_403(request, exception):
    return render(request, 'backend/errorhandler/403.html')


def error_404(request, exception):
    return render(request, 'backend/errorhandler/404.html')


def error_500(request):
    return render(request, 'backend/errorhandler/500.html')
