from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^new_bookings/', views.MemberBookingView.as_view(), name='member_booking'),
    url(r'^all_bookings/', views.AllBookings.as_view(), name='all_bookings'),
    url(r'^edit_bookings/(?P<booking_id>[0-9A-Fa-f-]+)/', views.EditBookings.as_view(), name='edit_bookings'),
    url(r'^secure_booking/(?P<booking_id>[0-9A-Fa-f-]+)/', views.approve_booking, name='secure_booking'),
    url(r'^select_bank/(?P<booking_id>[0-9A-Fa-f-]+)/', views.SelectBank.as_view(), name='select_bank'),
    url(r'^discount_booking/(?P<booking_id>[0-9A-Fa-f-]+)/', views.discount_booking, name='discount_booking'),

    url(r'^delete_booking/(?P<booking_id>[0-9A-Fa-f-]+)/', views.delete_booking, name='delete_booking'),
    url(r'^my_bookings/(?P<member_id>[0-9A-Fa-f-]+)/', views.MyBookings.as_view(), name='my_booking'),
    url(r'^ajax_load_cat/', views.load_ajax_cat, name='ajax_load_cat'),
    url(r'^ajax_load_unit/', views.load_ajax_unit, name='ajax_load_unit'),
    url(r'^load_booked_dates/', views.unit_booked_date, name='unit_booked_date'),
]