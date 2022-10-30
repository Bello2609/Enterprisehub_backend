# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views import generic
from .models import Register
from django.contrib import messages
from django.shortcuts import redirect

# Create your views here.


class ProgramRegistered(generic.ListView):
    model = Register
    template_name = 'backend/program/program_registered_list.html'


def mark_paid(request, reg_id):
    get_reg = Register.objects.get(id=reg_id)
    get_reg.p_status = True
    get_reg.save()
    messages.success(request, 'You marked a registration as valid')
    return redirect('program_registered_list')


def mark_un_paid(request, reg_id):
    get_reg = Register.objects.get(id=reg_id)
    get_reg.p_status = False
    get_reg.save()
    messages.warning(request, 'You marked a registration as in-valid')
    return redirect('program_registered_list')


def delete_registered(request, reg_id):
    get_reg = Register.objects.get(id=reg_id)
    get_reg.delete()
    messages.warning(request, 'You deleted a registration')
    return redirect('program_registered_list')

