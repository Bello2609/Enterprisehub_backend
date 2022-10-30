# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.views import generic
from .models import ResourceCenter
from .forms import ResourceCenterForm
from django.contrib import messages
from django.shortcuts import redirect

# Create your views here.


class NewResourceFile(generic.CreateView):
    template_name = 'backend/facility/resource_upload.html'
    model = ResourceCenter
    form_class = ResourceCenterForm

    def get_success_url(self):
        if self.kwargs['type'] == 'video':
            return reverse('resource_list', kwargs={'type': 'video'})
        elif self.kwargs['type'] == 'doc':
            return reverse('resource_list', kwargs={'type': 'doc'})
        else:
            return reverse('resource_list', kwargs={'type': 'link'})

    def get_context_data(self, **kwargs):
        context = super(NewResourceFile, self).get_context_data(**kwargs)
        context['type'] = self.kwargs['type']
        return context

    def form_valid(self, form):
        messages.success(self.request, 'New item added to resource center successfully')
        form.instance.uploaded_by_id = self.request.user.id
        if self.kwargs['type'] == 'video':
            form.instance.is_video = True
            form.instance.is_file = False
            form.instance.is_link = False

        elif self.kwargs['type'] == 'doc':
            form.instance.is_video = False
            form.instance.is_file = True
            form.instance.is_link = False
        else:
            form.instance.is_video = False
            form.instance.is_file = False
            form.instance.is_link = True
        form.save()
        return super(NewResourceFile, self).form_valid(form)


class ResourceList(generic.ListView):
    model = ResourceCenter
    template_name = 'backend/facility/resource_list.html'

    def get_context_data(self, **kwargs):
        context = super(ResourceList, self).get_context_data(**kwargs)
        context['video_list'] = ResourceCenter.objects.filter(is_video=True)
        context['file_list'] = ResourceCenter.objects.filter(is_file=True)
        context['link_list'] = ResourceCenter.objects.filter(is_link=True)
        context['resource_type'] = self.kwargs['type']
        return context


def delete_resource_file(request, resource_id, type):
    get_resource = ResourceCenter.objects.get(id=resource_id)
    get_resource.delete()

    messages.success(request, 'Item has been deleted successfully')
    if type == 'video':
        return redirect('resource_list', 'video')
    elif type == 'doc':
        return redirect('resource_list', 'doc')
    else:
        return redirect('resource_list', 'link')
