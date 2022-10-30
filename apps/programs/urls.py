
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^program_registered_list/$', views.ProgramRegistered.as_view(), name='program_registered_list'),
    url(r'^program_registered_mark/(?P<reg_id>[0-9A-Fa-f-]+)/$', views.mark_paid, name='mark_paid'),
    url(r'^program_registered_un_mark/(?P<reg_id>[0-9A-Fa-f-]+)/$', views.mark_un_paid, name='mark_un_paid'),
    url(r'^program_registered_delete/(?P<reg_id>[0-9A-Fa-f-]+)/$', views.delete_registered, name='delete_register'),
    ]