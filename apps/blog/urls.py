
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^new_blog_post/$', views.NewPostView.as_view(), name='new_post'),
    url(r'^all_blog_post/$', views.PostList.as_view(), name='post_list'),
    url(r'^edit_blog_posy/(?P<slug>[\w-]+)/$', views.PostEdit.as_view(), name='edit_blog_post'),
    url(r'^blog_post_delete/(?P<blog_id>[0-9A-Fa-f-]+)/$', views.delete_post, name='delete_post'),
    url(r'^blog_approve_post/(?P<blog_id>[0-9A-Fa-f-]+)/$', views.approve_post, name='approve_post'),
    url(r'^blog_dis_approve_post/(?P<blog_id>[0-9A-Fa-f-]+)/$', views.disapprove_post, name='disapprove_post'),

    # url(r'^reactivate/(?P<user_id>[0-9A-Fa-f-]+)/$', views.activate_staff, name='reactivate_staff'),


]