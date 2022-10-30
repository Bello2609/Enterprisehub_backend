# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView, ListView, DetailView, UpdateView
from ..members.forms import MemberShipRegistrationForm
from ..bookings.models import HeldBookings
from ..account.models import UserType
from .forms import CustomAuthForm, GuestBookForm
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from ..members.tokens import account_activation_token
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
from django.db import transaction
from ..membersite.models import MainSite, Portfolio
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from ..blog.models import NewPost
from ..facility.models import Information
from ..bookings.models import Bookings
from ..onboarding.models import GuestPaymentResource
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from .forms import ResendActivationForm
from ..members.models import Member
from ..members.views import post_credit_post_sagamy
from .models import GalleryPicture, GalleryCat
from ..account.models import HubGL
from .models import Testimonials, ClientLogo, FrontDesk
from .forms import TestimonialForm, ClientLogoForm, FrontDeskForm
from ..membersite.models import MainSite
from ..programs.models import Register, Programs
from ..programs.forms import ProgramRegisterForm
import random
# Create your views here.
from ..services.models import ProfessionalService
import requests


class LandingPage(TemplateView):
    template_name = 'index.html'


class WelcomePage(TemplateView):
    template_name = 'frontend/welcome.html'


class GalleryPage(TemplateView):
    template_name = 'frontend/new_front/gallery.html'

    def get_context_data(self, **kwargs):
        context = super(GalleryPage, self).get_context_data(**kwargs)
        context['gallery_image'] = GalleryPicture.objects.all()
        context['galley_cat'] = GalleryCat.objects.all()
        return context


class InformationView(DetailView):
    template_name = 'frontend/info.html'
    model = Information


class HomePage(TemplateView):
    template_name = 'frontend/new_front/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        context['blog_post'] = NewPost.objects.filter(publish=1).order_by('-id')[:3]
        context['blog_count'] = NewPost.objects.filter(publish=1).count()
        context['testimonial'] = Testimonials.objects.all()
        logo = ClientLogo.objects.all()
        context['client_logo'] = logo
        return context


class ContactPage(TemplateView):
    template_name = 'frontend/new_front/contact.html'


class AboutPage(TemplateView):
    template_name = 'frontend/new_front/about.html'

    def get_context_data(self, **kwargs):
        context = super(AboutPage, self).get_context_data(**kwargs)
        context['clients'] = None
        context['testimonial'] = Testimonials.objects.all()
        logo = ClientLogo.objects.all()
        context['client_logo'] = logo
        return context


class ServicePage(TemplateView):
    template_name = 'frontend/new_front/services.html'


class ProfessionalServicesView(TemplateView):
    template_name = 'frontend/new_front/prof_services.html'

    def get_context_data(self, **kwargs):
        context = super(ProfessionalServicesView, self).get_context_data(**kwargs)
        context['prof_services'] = ProfessionalService.objects.all()
        context['testimonial'] = Testimonials.objects.all()
        return context


class PricingPage(TemplateView):
    template_name = 'frontend/pricing-table.html'


class MemberRegister(CreateView):
    template_name = 'frontend/register_member.html'
    form_class = MemberShipRegistrationForm
    success_url = reverse_lazy('register_member')
    model = Member
    password = User.objects.make_random_password()

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.member_id = random.randrange(1, 1234567890, 5)
            form.save()
            create_user = User.objects.create_user(
                username=form.instance.username,
                password=self.password,
                first_name=form.instance.first_name,
                last_name=form.instance.last_name,
                email=form.instance.email,
                is_active=False,
            )
            create_user.save()
            create_account_type = UserType.objects.create(account_type=1, user_id=create_user.id)
            create_account_type.save()

            group, created = Group.objects.get_or_create(name='member')
            group.user_set.add(create_user.id)

            message = render_to_string('emails/account_activation_email.html', {
                'user': form.instance.username,
                'domain': get_current_site(self.request).domain,
                'uid': urlsafe_base64_encode(force_bytes(create_user.id)),
                'token': account_activation_token.make_token(create_user),
                'password': self.password
            })
            mail_subject = 'Welcome Enterprise Hubs, Please activate you email'
            to_email = form.instance.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()

            messages.success(self.request, 'Your Registration was successful. Please kindly validate your emails.')
        return super(MemberRegister, self).form_valid(form)


def resend_activation_email(request):
    if request.method == 'POST':
        form = ResendActivationForm(request.POST)
        if form.is_valid():
            try:
                get_user = User.objects.get(email__exact=form.cleaned_data['email'], is_active=False)
                try:
                    member = Member.objects.get(email__exact=form.cleaned_data['email'], validated=False)
                    password = User.objects.make_random_password()
                    current_site = str(get_current_site(request).domain)

                    message = render_to_string('emails/account_activation_email.html', {
                        'user': member.username,
                        'domain': current_site,
                        'uid': urlsafe_base64_encode(force_bytes(get_user.id)),
                        'token': account_activation_token.make_token(get_user),
                        'password': password
                    })
                    mail_subject = 'Welcome Enterprise Hubs, Please activate you email'
                    to_email = form.cleaned_data['email']
                    send_email = EmailMessage(mail_subject, message, to=[to_email])
                    send_email.content_subtype = 'html'
                    send_email.send()

                    get_user.set_password(password)
                    get_user.save()

                    messages.success(request, 'Activation link has been resent. Please activate your email')
                    return redirect('resend_activation_link')
                except Member.DoesNotExist:
                    messages.warning(request, 'Internal System Error. This operation cannot be completed')
            except User.DoesNotExist:
                messages.warning(request, 'Internal System Error: Activation link cannot be sent.')
    else:
        form = ResendActivationForm()
    return render(request, 'registration/resend_activation.html', {'form': form})


class Login(FormView):
    template_name = 'registration/login.html'
    form_class = CustomAuthForm


class GuestBooking(CreateView):
    template_name = 'frontend/guest_booking.html'
    form_class = GuestBookForm
    model = Bookings

    def get_success_url(self):

        return reverse_lazy('guest_booking_success', args=[self.object.facility_id, self.object.id, '0'])

    def form_valid(self, form):
        with transaction.atomic():
            book_date = datetime.strptime(str(form.instance.book_from), '%Y-%m-%d')
            form.instance.is_member = False
            form.save()

            if self.request.POST.get('book_to'):
                end_date = datetime.strptime(str(form.instance.book_to), '%Y-%m-%d')
                delta = end_date - book_date

                for i in range(delta.days + 1):

                    held_book_range = HeldBookings.objects.create(
                        booking_id=form.instance.id,
                        date=book_date + timedelta(i),
                        unit_id=form.instance.unit_id
                    )
                    held_book_range.save()
            else:
                held_book_range = HeldBookings.objects.create(
                    booking_id=form.instance.id,
                    date=book_date,
                    unit_id=form.instance.unit_id
                )
                held_book_range.save()

            message = render_to_string('emails/guest_booking_email.html', {
                'name': form.instance.guest_name,
                'booked_facility': form.instance.facility,
                'booked_category': form.instance.category,
                'booked_unit': form.instance.unit,
                'book_from': form.instance.book_from,
                'book_to': form.instance.book_to,
                'amount_payable': form.instance.payable,
                'booking_id': form.instance.id,
            })
            mail_subject = 'Enterprise Hubs Booking Confirmation'
            to_email = form.instance.guest_email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send(fail_silently=True)


            # Send Admin Email
            admin_subject = "New guest booking"
            admin_msg = f"You have a new member booking from {form.instance.guest_name} with order ID {form.instance.id}"
            admin_emails = ["danlanko1@gmail.com", "info@enterprisehubs.com"]
            send_email = EmailMessage(admin_subject, admin_msg, to=admin_emails)
            send_email.content_subtype = 'html'
            send_email.send(fail_silently=True)
            messages.success(self.request, 'Your bookings has been created')

        return super(GuestBooking, self).form_valid(form)


class GuessBookingSuccess(DetailView):
    template_name = 'frontend/guest_booking_success.html'
    pk_url_kwarg = 'booking_id'
    model = Bookings


def guest_payment_resources(request, booking_id):
    get_booking = Bookings.objects.get(id=booking_id)
    ref_id = random.randrange(0, 9876543210, 4)
    GuestPaymentResource.objects.create(
        status=False,
        booking_id=booking_id,
        amount=get_booking.payable,
        ref_id=ref_id
    )

    return render(request, 'frontend/guest_booking_success.html', {'object': get_booking, 'ref_id': ref_id})


def verify_guest_payment(request, ref_id, booking_id):
    headers = {"Content-Type": 'application/json', "Authorization": "Bearer " + settings.PAYSTACK_KEY}
    response = requests.get('https://api.paystack.co/transaction/verify/' + ref_id, headers=headers)
    pay_stack = response.json()
    status = pay_stack['status']
    pay_stack_message = pay_stack['message']
    get_book_ref = GuestPaymentResource.objects.get(ref_id=ref_id)
    get_booking = Bookings.objects.get(id=booking_id)

    with transaction.atomic():
        if status is True:
            get_book_ref.status = True
            get_book_ref.save()

            get_booking.is_secured = True
            get_booking.save()

            message = render_to_string('emails/booking_payment_received.html', {
                'user': get_booking.guest_name,
                'booked_facility': get_booking.facility,
                'booked_category': get_booking.category,
                'booked_unit': get_booking.unit,
                'book_from': get_booking.book_from,
                'book_to': get_booking.book_to,
                'booking_id': booking_id,
            })
            mail_subject = 'Enterprise Hubs Booking Payment Received'
            to_email = get_booking.guest_email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html'
            send_email.send()

            # post_credit_post_sagamy(
            #     request,
            #     facility_id=get_booking.facility_id,
            #     ref_id=booking_id,
            #     guest_name=get_booking.guest_name,
            #     guest_phone=get_booking.guest_phone,
            #     amount=get_booking.payable,
            #     pay_mode=3,
            #     account=HubGL.objects.get(category_id=get_booking.category_id).acc_no,
            #     member_id=0,
            #     trans_type='makes of booking of NGN %s' % get_booking.payable,
            #     debit_account='1110'
            # )

            messages.success(request, 'Your payment has been received, and your booking is secured')

        else:
            messages.error(request, 'Error!!!, Payment unsuccessful with error message: %s' % pay_stack_message)
        return redirect('guest_booking_success', get_booking.facility_id, get_booking.id)


class BlogList(ListView):
    template_name = 'frontend/new_front/blog.html'
    model = NewPost
    queryset = NewPost.objects.filter(publish=True).order_by('-id')


class BlogDetail(DetailView):
    model = NewPost
    template_name = 'frontend/new_front/single_blog.html'

    def get_context_data(self, **kwargs):
        context = super(BlogDetail, self).get_context_data(**kwargs)
        context['latest_blog'] = NewPost.objects.filter(publish=1).order_by('-id')[:10]
        return context


class MemberWebSpace(DetailView):
    model = MainSite
    template_name = 'frontend/member_site.html'

    def get_context_data(self, **kwargs):
        context = super(MemberWebSpace, self).get_context_data(**kwargs)
        context['portfolio'] = Portfolio.objects.filter(member_id=self.object.member_id)
        return context


class TestimonialUpload(CreateView):
    model = Testimonials
    form_class = TestimonialForm
    template_name = 'backend/onboarding/new_test_logo.html'
    success_url = reverse_lazy('testimonial_list')

    def form_valid(self, form):
        messages.success(self.request, 'New Testimonial has been saved.')
        return super(TestimonialUpload, self).form_valid(form)


class TestimonialUpdate(UpdateView):
    model = Testimonials
    form_class = TestimonialForm
    template_name = 'backend/onboarding/new_test_logo.html'
    pk_url_kwarg = 'test_id'
    success_url = reverse_lazy('testimonial_list')

    def form_valid(self, form):
        messages.success(self.request, 'Testimonial has been updated.')
        return super(TestimonialUpdate, self).form_valid(form)


class TestimonialList(ListView):
    model = Testimonials
    template_name = 'backend/onboarding/all_testimonials.html'


def delete_testimonial(request, test_id):
    get_test = Testimonials.objects.get(id=test_id)
    get_test.delete()
    messages.success(request, 'Delete action was successfull')
    return redirect('testimonial_list')


class ClientLogoUpload(CreateView):
    model = ClientLogo
    form_class = ClientLogoForm
    template_name = 'backend/onboarding/client_logo_upload.html'
    success_url = reverse_lazy('client_logo_list')

    def form_valid(self, form):
        messages.success(self.request, 'New Client Logo has been saved.')
        return super(ClientLogoUpload, self).form_valid(form)


class ClientLogoList(ListView):
    model = ClientLogo
    template_name = 'backend/onboarding/client_logo_list.html'


def delete_client_logo(request, c_logo_id):
    get_logo = ClientLogo.objects.get(id=c_logo_id)
    get_logo.delete()
    messages.success(request, 'Delete action was successfull')
    return redirect('client_logo_list')


def search_word(request):
    search = request.GET['search-word']
    listings = MainSite.objects.filter(business_name__icontains=search).exclude(image__exact='').exclude(image__isnull=True)
    return render(request, 'frontend/business_directory.html', {'listings': listings, 'search': True})


class BusinessDirectoryListing(TemplateView):
    template_name = 'frontend/new_front/business_listings.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessDirectoryListing, self).get_context_data(**kwargs)
        context['listings'] = MainSite.objects.exclude(image__exact='').exclude(image__isnull=True)
        return context


class ProgramRegisterList(ListView):
    model = Programs
    template_name = 'frontend/program_list.html'


class ProgramRegister(CreateView):
    model = Register
    template_name = 'frontend/program_register.html'
    form_class = ProgramRegisterForm

    def get_success_url(self):
        return reverse_lazy('program_register', args=[self.kwargs['slug'], self.kwargs['program_id']])

    def get_context_data(self, **kwargs):
        context = super(ProgramRegister, self).get_context_data(**kwargs)
        context['object'] = Programs.objects.get(id=self.kwargs['program_id'])
        return context

    def form_valid(self, form):
        form.instance.program_id = self.kwargs['program_id']
        messages.success(self.request, 'Your registration is successful')
        return super(ProgramRegister, self).form_valid(form)


class FrontDeskView(CreateView):
    form_class = FrontDeskForm
    template_name = 'frontend/front_desk.html'
    model = FrontDesk
    success_url = reverse_lazy('visitors')

    def form_valid(self, form):
        messages.success(self.request, 'Thank you %s for completing our visitors form. Have a splendid tour around our'
                                       ' premises' % form.instance.name)
        return super(FrontDeskView, self).form_valid(form)


class Franchise(TemplateView):
    template_name = 'frontend/new_front/franchise.html'


def post_service(request, s_type):
    name = request.POST.get('name')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    if name is None or phone is None or email is None:
        messages.error(request, f"Something went wrong, please contact admin")
    else:
        mail_subject = 'Enterprise Hubs Service Enquiry'
        to_email = ["info@enterprisehubs.com", "dozie@pedestalafrica.com", "danlanko1@gmail.com"]
        message = f"You have a new {s_type} service enquiry from {name} - {email} - {phone}"
        send_email = EmailMessage(mail_subject, message, to=to_email)
        send_email.content_subtype = 'html'
        send_email.send()
        messages.success(request, f"Thank you {name}, we have received your service enquiry, "
                                  f"one of our representative will contact you shortly.")
    return redirect('prof_services')


class LocationAbuja(TemplateView):
    template_name = 'frontend/new_front/abuja.html'


class LocationLagos(TemplateView):
    template_name = 'frontend/new_front/lagos.html'


class LocationKano(TemplateView):
    template_name = 'frontend/new_front/kano.html'