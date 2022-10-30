
from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomAuthForm, CustomPassResetForm, CustomPasswordResetForm


urlpatterns = [
    url(r'^$', views.WelcomePage.as_view(), name='welcome_page'),
    url(r'^homepage/$', views.HomePage.as_view(), name='home_page'),
    # url(r'^$', views.LandingPage.as_view(), name='landing_page'),
    url(r'^gallery/$', views.GalleryPage.as_view(), name='gallery_page'),
    url(r'^contact/$', views.ContactPage.as_view(), name='contact_page'),
    url(r'^information/(?P<slug>[\w-]+)/$', views.InformationView.as_view(), name='information'),
    url(r'^about/$', views.AboutPage.as_view(), name='about_page'),
    url(r'^location/abuja/$', views.LocationAbuja.as_view(), name='abuja'),
    url(r'^location/lagos/$', views.LocationLagos.as_view(), name='lagos'),
    url(r'^location/kano/$', views.LocationKano.as_view(), name='kano'),


    url(r'^business_directory/$', views.BusinessDirectoryListing.as_view(), name='business)_directory'),
    url(r'^franchising/$', views.Franchise.as_view(), name='franchise'),
    url(r'^search/$', views.search_word, name='search'),

    url(r'^programs/$', views.ProgramRegisterList.as_view(), name='program_list'),
    url(r'^programs_register/(?P<slug>[\w-]+)(?P<program_id>[0-9A-Fa-f-]+)/$', views.ProgramRegister.as_view(), name='program_register'),

    url(r'^visitors_form/$', views.FrontDeskView.as_view(), name='visitors'),

    url(r'^client_logo/$', views.ClientLogoUpload.as_view(), name='new_client_logo'),
    url(r'^client_logo_list/$', views.ClientLogoList.as_view(), name='client_logo_list'),
    url(r'^client_logo_delete/(?P<c_logo_id>[0-9A-Fa-f-]+)/$', views.delete_client_logo, name='client_logo_delete'),

    url(r'^new_testimonial/$', views.TestimonialUpload.as_view(), name='new_testimonial'),
    url(r'^testimonial_list/$', views.TestimonialList.as_view(), name='testimonial_list'),
    url(r'^testimonial_delete/(?P<test_id>[0-9A-Fa-f-]+)/$', views.delete_testimonial, name='testimonial_delete'),
    url(r'^testimonial_update/(?P<test_id>[0-9A-Fa-f-]+)/$', views.TestimonialUpdate.as_view(), name='testimonial_update'),

    url(r'^services/$', views.ServicePage.as_view(), name='service_page'),
    url(r'^professional_services/$', views.ProfessionalServicesView.as_view(), name='prof_services'),
    url(r'^post_service/(?P<s_type>[^/]+)/?$', views.post_service, name='post_service'),

    url(r'^pricing/$', views.PricingPage.as_view(), name='pricing_page'),
    url(r'^all_blog/', views.BlogList.as_view(), name='all_blog_post'),
    url(r'^blog_details/(?P<slug>[\w-]+)/$', views.BlogDetail.as_view(), name='blog_details'),
    url(r'^resend_activation_link/$', views.resend_activation_email, name='resend_activation_link'),
    url(r'^member_registration/$', views.MemberRegister.as_view(), name='register_member'),
    url(r'^guest_bookings/$', views.GuestBooking.as_view(), name='guest_booking'),
    url(r'^booking_success/(?P<facility_id>[0-9A-Fa-f-]+)-(?P<booking_id>[0-9A-Fa-f-]+)-(?P<slug>[\w-]+)/$', views.GuessBookingSuccess.as_view(),
        name='guest_booking_success'),
    url(r'^guest_payment_resources/(?P<booking_id>[0-9A-Fa-f-]+)/$', views.guest_payment_resources,
        name='guest_payment_resources'),
    url(r'^verify_guest_payment/(?P<ref_id>[0-9A-Fa-f-]+)-(?P<booking_id>[0-9A-Fa-f-]+)/$', views.verify_guest_payment,
        name='guest_verify_payment'),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login', kwargs={"authentication_form": CustomAuthForm}),
    url(r'^accounts/login/$', auth_views.LoginView.as_view(), name='login', kwargs={"authentication_form": CustomAuthForm}),
    url(r'^logout/$', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout'),
    url(r'^(?P<slug>[\w-]+)/$', views.MemberWebSpace.as_view(), name='member_web_space'),
    url(r'^accounts/password_reset/$', auth_views.PasswordResetView.as_view(), name='pass_reset', kwargs={"password_reset_form": CustomPassResetForm}),
    url(r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm', kwargs={'set_password_form': CustomPasswordResetForm }),

]