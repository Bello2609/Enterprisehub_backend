# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import NewPost
from .forms import NewPostForm
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required

# Create your views here.


class NewPostView(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
    model = NewPost
    template_name = 'backend/blog/new_post.html'
    form_class = NewPostForm
    success_url = reverse_lazy('new_post')
    raise_exception = True
    permission_required = 'blog.add_newpost'

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.user_id = self.request.user.id
            form.save()
            messages.success(self.request, 'Success, new post was created.')
        return super(NewPostView, self).form_valid(form)


class PostList(LoginRequiredMixin, PermissionRequiredMixin,  generic.ListView):
    model = NewPost
    template_name = 'backend/blog/all_post.html'
    raise_exception = True
    permission_required = 'blog.add_newpost'


class PostEdit(LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView):
    model = NewPost
    template_name = 'backend/blog/new_post.html'
    form_class = NewPostForm
    success_url = reverse_lazy('post_list')
    raise_exception = True
    permission_required = 'blog.change_newpost'

    def form_valid(self, form):
        with transaction.atomic():
            today = datetime.today()
            form.instance.last_edited = today
            form.instance.edited_by_id = self.request.user.id
            form.save()
            messages.success(self.request, 'You post was edited successfully')
        return super(PostEdit, self).form_valid(form)


@login_required()
@permission_required('blog.delete_newpost', raise_exception=True)
def delete_post(request, blog_id):
    get_blog = NewPost.objects.get(id=blog_id)
    get_blog.delete()
    messages.success(request, 'Post deleted successfully')
    return redirect('post_list')


@login_required()
@permission_required('blog.approve_post', raise_exception=True)
def approve_post(request, blog_id):
    get_blog = NewPost.objects.get(id=blog_id)
    get_blog.publish = True
    get_blog.save()
    messages.success(request, 'Blog Post Approved successfully')
    return redirect('post_list')


@login_required()
@permission_required('blog.approve_post', raise_exception=True)
def disapprove_post(request, blog_id):
    get_blog = NewPost.objects.get(id=blog_id)
    get_blog.publish = False
    get_blog.save()
    messages.success(request, 'Blog Post Dis-Approved successfully')
    return redirect('post_list')