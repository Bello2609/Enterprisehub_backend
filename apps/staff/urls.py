
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^new_staff/', views.NewStaff.as_view(), name='new_staff'),
    url(r'^all_staff/', views.StaffList.as_view(), name='all_staff'),
    url(r'^edit_staff/(?P<staff_id>[0-9A-Fa-f-]+)/$', views.UpdateStaff.as_view(), name='update_staff'),
    url(r'^deactivated/(?P<user_id>[0-9A-Fa-f-]+)/$', views.deactivate_staff, name='deactivate_staff'),
    url(r'^staff_log/', views.StaffActivityLog.as_view(), name='staff_log'),
    url(r'^reactivate/(?P<user_id>[0-9A-Fa-f-]+)/$', views.activate_staff, name='reactivate_staff'),
    url(r'^staff_details/(?P<facility_id>[0-9A-Fa-f-]+)/(?P<staff_id>[0-9A-Fa-f-]+)/$', views.StaffDetails.as_view(),
        name='staff_details'),
    url(r'^update_self/(?P<facility_id>[0-9A-Fa-f-]+)-(?P<staff_id>[0-9A-Fa-f-]+)/$', views.UpdateSelf.as_view(),
        name='update_self'),

]