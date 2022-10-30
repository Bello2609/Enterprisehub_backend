
from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^dashboard/$', views.Dashboard.as_view(), name='dashboard'),
    url(r'^forum/$', views.ForumView.as_view(), name='forum'),
    url(r'^login_success/$', views.login_success, name='login_success'),
    url(r'^change_password/$', views.change_password, name='change_password'),


]