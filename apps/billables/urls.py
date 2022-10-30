
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^credit_member/', views.CreditMember.as_view(), name='credit_member'),
    url(r'^recent_credit/', views.AllCredit.as_view(), name='all_credit'),
    url(r'^revert_transaction/(?P<trans_id>[0-9A-Fa-f-]+)/$', views.revert_transaction, name='revert_transaction'),

]