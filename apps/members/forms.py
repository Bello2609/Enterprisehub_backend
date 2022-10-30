from django import forms
from .models import Member, CentralDatabase
from django.contrib.auth.models import User
from .models import MembershipType


class MemberShipRegistrationForm(forms.ModelForm):

    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'type', 'username', 'gender',
                  'business_name', 'designation', 'accept_tc', 'valid_id', 'cac']

        widgets = {
            'type': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Type'}),
            'gender': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Gender'}),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'First Name * ', }),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Last Name *', }),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'Email *'}),
            'phone': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Phone *'}),
            'username': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Username *'}),
            'business_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Company Name *'}),
            'designation': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Designation *'}),
            'address': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Address *'}),

        }

    def clean(self):
        cleaned_data = super(MemberShipRegistrationForm, self).clean()

        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        type_id = cleaned_data.get('type')

        if User.objects.filter(username=username).exists():
            msg = 'Username is taken'
            self.add_error('username', msg)

        if User.objects.filter(email=email).exists():
            msg = 'A member exist with this email'
            self.add_error('email', msg)

        if cleaned_data.get('accept_tc') is False:
            msg = 'You must accept our T&C to register'
            self.add_error('accept_tc', msg)

        if not cleaned_data.get('cac'):
            try:
                if MembershipType.objects.get(name=type_id).id == 3:
                    msg = 'To register as a black member, CAC document must be uploaded'
                    self.add_error('cac', msg)
            except MembershipType.DoesNotExist:
                pass

        return cleaned_data


class MemberShipUpdateForm(forms.ModelForm):

    class Meta:
        model = Member
        fields = ['date_joined', 'last_pay_date', 'expire_date', 'first_name', 'last_name', 'phone', 'address', 'image', 'cac', 'valid_id']

        widgets = {
            'first_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'First Name', }),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Last Name', }),
            'phone': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'date_joined': forms.TextInput(
                attrs={'class': 'form-control'}),
            'last_pay_date': forms.TextInput(
                attrs={'class': 'form-control'}),
            'expire_date': forms.TextInput(
                attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(),
            'cac': forms.ClearableFileInput(),
            'valid_id': forms.ClearableFileInput()
        }


class MemberUpdateSelfForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['phone', 'image']

        widgets = {
            'phone': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'image': forms.ClearableFileInput()
        }


class ChangePackageType(forms.ModelForm):

    class Meta:
        model = Member
        fields = ('upgrade_type',)

        widgets = {
            'upgrade_type': forms.Select(attrs={'class': 'form-control', 'type': 'select', 'required': 'required'}),
        }


class CreditSelfForm(forms.Form):

    amount = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Amount', 'required': 'required'}))


class ResourceCenterForm(forms.ModelForm):

    class Meta:
        model = CentralDatabase
        exclude = {'owned_by'}
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Title', }),
            'docs': forms.ClearableFileInput(
                attrs={'required': 'required'}
            )
        }