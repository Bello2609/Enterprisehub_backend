
from django.conf.urls import url
from django.urls import path
from . import views


urlpatterns = [
    url(r'^new_member/$', views.NewMember.as_view(), name='new_member'),
    url(r'^all_members/$', views.MemberList.as_view(), name='all_members'),
    url(r'^visiting_client_list/', views.VisitingCustomerList.as_view(), name='visiting_clients'),
    url(r'^edit_members/(?P<member_id>[0-9A-Fa-f-]+)/$', views.UpdateMember.as_view(), name='update_members'),
    url(r'^activate_member_account/(?P<member_id>[0-9A-Fa-f-]+)/$', views.activate_member_account, name='activate_member'),
    url(r'^block_member/(?P<member_id>[0-9A-Fa-f-]+)/$', views.deactivate_member, name='deactivate_member'),
    url(r'^activate_member/(?P<member_id>[0-9A-Fa-f-]+)/$', views.activate_member, name='reactivate_member'),
    url(r'^member_account_settings/(?P<member_id>[0-9A-Fa-f-]+)/$', views.MemberAccount.as_view(), name='member_account'),
    url(r'^credit_wallet/$', views.CreditSelf.as_view(), name='credit_self'),

    url(r'^override_membership/(?P<member_id>[0-9A-Fa-f-]+)/$', views.manual_membership_activation, name='manual_override'),
    path('generate_sheet/<from_date>/<to_date>/<sheet_type>', views.generate_report_sheet, name='generate_sheet'),

    url(r'^payment_resources/(?P<member_id>[0-9A-Fa-f-]+)/(?P<t_type>.+?)/(?P<amount>[0-9A-Fa-f-]+)/$', views.payment_resources,
        name='payment_resources'),
    url(r'^verify_payment/(?P<member_id>[0-9A-Fa-f-]+)/(?P<ref_id>[0-9A-Fa-f-]+)/(?P<t_type>.+?)/$', views.verify_payment,
        name='verify_payment'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^member_details/(?P<member_id>[0-9A-Fa-f-]+)/$', views.MemberDetails.as_view(), name='member_details'),
    url(r'^member_self_update/(?P<member_id>[0-9A-Fa-f-]+)/$', views.UpdateMemberSelf.as_view(), name='member_self_update'),
    url(r'^member_delete/(?P<member_id>[0-9A-Fa-f-]+)/$', views.delete_member, name='member_delete'),
    url(r'^central_database_upload/', views.CentralDB.as_view(), name='central_database_upload'),
    url(r'^central_database_list/(?P<member_id>[0-9A-Fa-f-]+)/$', views.CentralDBList.as_view(), name='central_database_list'),
    url(r'^central_database_delete/(?P<item_id>[0-9A-Fa-f-]+)/$', views.central_db_delete, name='central_database_delete'),
]