from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^select_services/(?P<a_type>[\w-]+)/$', views.SelectService.as_view(), name='select_service'),
    url(r'^all_booked_services/', views.ServiceBookingList.as_view(), name='service_booking_list'),
    url(r'^book_services/(?P<service_cat_id>[0-9A-Fa-f-]+)/(?P<a_type>[\w-]+)/$', views.service_booking,
        name='service_booking'),
    url(r'^view_book_services/(?P<service_id>[0-9A-Fa-f-]+)/$', views.ViewBookedServices.as_view(),
        name='view_booked_services'),
    url(r'^print_booked_service/(?P<service_id>[0-9A-Fa-f-]+)/$', views.PrintBookedServices.as_view(),
        name='print_book_services'),
    url(r'^service_pay_later/(?P<member_id>[0-9A-Fa-f-]+)/(?P<service_book_id>[0-9A-Fa-f-]+)/$',
        views.service_pay_later, name='pay_later'),
    url(r'^delete_services/(?P<service_book_id>[0-9A-Fa-f-]+)/$', views.service_delete, name='service_delete'),
    url(r'^complete/(?P<service_book_id>[0-9A-Fa-f-]+)/$', views.complete_service, name='complete_service'),


]