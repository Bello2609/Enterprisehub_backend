
from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^build_web_space/$', views.BuildMyWebSpace.as_view(), name='build_web_space'),
    url(r'^view_my_space/(?P<member_id>[0-9A-Fa-f-]+)/$', views.ViewMyWebSpace.as_view(), name='view_my_web_space'),
    url(r'^portal_request/(?P<member_id>[0-9A-Fa-f-]+)/$', views.request_setup, name='request_setup'),
    url(r'^edit_my_space/(?P<web_space_id>[0-9A-Fa-f-]+)/$', views.UpdateMyWebSpace.as_view(), name='edit_my_web_space'),
    url(r'^create_portfolio/$', views.CreatePortfolio.as_view(), name='create_portfolio'),
    url(r'^delete_portfolio/(?P<portfolio_id>[0-9A-Fa-f-]+)/$', views.delete_portfolio, name='delete_portfolio'),

]