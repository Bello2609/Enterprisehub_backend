from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^new_resource_file/(?P<type>[\w-]+)/$', views.NewResourceFile.as_view(), name='new_resource_file'),
    url(r'^resource_list/(?P<type>[\w-]+)/$', views.ResourceList.as_view(), name='resource_list'),
    url(r'^delete_resource/(?P<resource_id>[0-9A-Fa-f-]+)/(?P<type>[\w-]+)/$', views.delete_resource_file, name='delete_resource')
    ]


