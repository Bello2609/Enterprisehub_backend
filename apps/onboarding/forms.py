from django import forms
from ..members.models import Member
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.forms.widgets import PasswordInput, TextInput
from ..bookings.models import Bookings, HeldBookings
from ..facility.models import Category, Unit
from datetime import timedelta, date
from .models import Testimonials, ClientLogo, FrontDesk


class CustomPassResetForm(PasswordResetForm):
    """
    Reset Password Form
    """
    email = forms.EmailField(widget=TextInput(attrs={'name': 'username', 'class': 'form-control',
                                                     'type': 'email', 'id': 'username', 'placeholder': 'Email'}))


class CustomPasswordResetForm(SetPasswordForm):
    """
       Change Password Form
    """
    new_password1 = forms.CharField(widget=PasswordInput(attrs={'name': 'password1',
                                                                'class': 'form-control input-height col-md-3',
                                                                'type': 'password', 'id': 'new-password1',
                                                                'placeholder': 'New Password'}))
    new_password2 = forms.CharField(widget=PasswordInput(attrs={'name': 'password2',
                                                                'class': 'form-control input-height col-md-3',
                                                                'type': 'password', 'id': 'new-password2',
                                                                'placeholder': 'Confirm Password'}))


class ResendActivationForm(forms.Form):
    email = forms.EmailField(required=True, widget=TextInput(attrs={'name': 'username', 'class': 'form-control',
                                                     'type': 'email', 'id': 'username', 'placeholder': 'Email'}))


class GuestBookForm(forms.ModelForm):

    class Meta:
        model = Bookings
        fields = ['unit', 'book_from', 'facility', 'category', 'book_to', 'guest_name', 'guest_email', 'guest_phone']

        widgets = {

            'facility': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select'}),
            'category': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select'}),
            'unit': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select'}),
            'guest_name': forms.TextInput(attrs={'name': 'guest_name', 'class': 'form-control',
                                                 'placeholder': 'Enter Name', 'required': 'required'}),
            'guest_email': forms.EmailInput(attrs={'name': 'guest_email', 'class': 'form-control',
                                                 'placeholder': 'Enter Email', 'required': 'required'}),
            'guest_phone': forms.NumberInput(attrs={'name': 'guest_phone', 'class': 'form-control',
                                                   'placeholder': 'Enter Phone', 'required': 'required'}),
            'book_from': forms.DateInput(attrs={'class': 'form-group form-control input-height datepicker',
                                                'placeholder': 'Pick a date'}),
            'book_to': forms.DateInput(attrs={'class': 'form-group form-control input-height datepicker',
                                              'placeholder': 'Pick a date'}),
        }

    def clean(self):
        cleaned_data = super(GuestBookForm, self).clean()
        today = date.today()
        booking_date = cleaned_data.get('book_from')
        end_date = cleaned_data.get('book_to')
        unit = cleaned_data.get('unit')

        # if booking_date < today:
        #     raise forms.ValidationError({'book_from': ['Input Error...Date cannot be in the past']})
        #
        # if end_date:
        #
        #     if end_date <= booking_date:
        #         raise forms.ValidationError({
        #             'book_to': ['Input Error...Book_to: cannot be less than or equal to book_from']
        #         })

        if Bookings.objects.filter(is_hold=1, unit_id=unit).exists():

            if end_date:
                delta = end_date - booking_date

                for i in range(delta.days + 1):

                    try:
                        if HeldBookings.objects.get(date=booking_date + timedelta(i), unit_id=unit):
                            raise forms.ValidationError(
                                'Input Error. Selected dates is clashing with another booking')
                    except HeldBookings.DoesNotExist:
                        pass
            else:
                try:
                    if HeldBookings.objects.get(date=booking_date, unit_id=unit):
                        raise forms.ValidationError({
                            'book_from': ['Input Error... Date Collision, Please select only selectable dates.']
                        })

                except HeldBookings.DoesNotExist:
                    pass

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(GuestBookForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.none()
        self.fields['unit'].queryset = Unit.objects.none()

        if 'facility' in self.data:
            try:

                facility_id = str(self.data.get('facility'))

                self.fields['category'].queryset = Category.objects.filter(facility_id=facility_id)

            except (ValueError, TypeError):

                pass  # invalid input from the client; ignore and fallback to empty Matter queryset

        elif self.instance.id:

            self.fields['category'].queryset = Category.objects.filter(facility_id=self.instance.id)

        if 'category' in self.data:
            try:
                category_id = str(self.data.get('category'))

                self.fields['unit'].queryset = Unit.objects.filter(category_id=category_id)

            except (ValueError, TypeError):

                pass

        elif self.instance.id:

            self.fields['unit'].queryset = Unit.objects.filter(category_id=self.instance.id)


class CustomAuthForm(AuthenticationForm):
    """
    Login Form
    """
    username = forms.CharField(widget=TextInput(attrs={'name': 'username', 'class': 'form-control',
                                                       'placeholder': 'Username'}))
    password = forms.CharField(widget=PasswordInput(attrs={'name': 'password', 'class': 'form-control',
                                                           'type': 'password', 'placeholder': 'Password'}))


class MemberShipRegistrationForm(forms.ModelForm):

    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'type', 'image', 'username']

        widgets = {
            'type': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select Client'}),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'First Name', }),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Last Name', }),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'username': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'image': forms.ClearableFileInput()
        }

    def clean(self):
        cleaned_data = super(MemberShipRegistrationForm, self).clean()

        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if User.objects.filter(username=username).exists():
            msg = 'Username is taken'
            self.add_error('username', msg)
        if User.objects.filter(email=email).exists():
            msg = 'This email is already in our Database. Please use the forgot password link'
            self.add_error('email', msg)

        return cleaned_data


class TestimonialForm(forms.ModelForm):

    class Meta:
        model = Testimonials
        fields = '__all__'

        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Name', }),
            'company': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Company', }),
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'What did the member say?'}),
            'image': forms.ClearableFileInput()
        }


class ClientLogoForm(forms.ModelForm):

    class Meta:
        model = ClientLogo
        fields = '__all__'

        widgets = {
            'client_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Company Name', }),
            'url': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Company URL', }),
            'logo': forms.ClearableFileInput()
        }


class FrontDeskForm(forms.ModelForm):

    class Meta:
        model = FrontDesk
        fields = '__all__'

    def __init__(self,  *args, **kwargs):
        super(FrontDeskForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.replace('_', ' ').title(),
            })

