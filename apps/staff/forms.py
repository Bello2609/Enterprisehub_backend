from django import forms
from .models import StaffModel
from django.contrib.auth.models import User


class CreateStaffForm(forms.ModelForm):

    class Meta:
        model = StaffModel
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'staff_type', 'image', 'username', 'facility']

        widgets = {
            'facility': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select '}),
            'staff_type': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select '}),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'First Name', }),
            'username': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Username', }),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Last Name', }),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'image': forms.ClearableFileInput()
        }

    def clean(self):
        cleaned_data = super(CreateStaffForm, self).clean()

        username = cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            msg = 'Username is taken'
            self.add_error('username', msg)

        return cleaned_data


class UpdateStaffForm(forms.ModelForm):
    class Meta:
        model = StaffModel
        fields = ['first_name', 'last_name', 'phone', 'address', 'staff_type', 'image', 'facility']

        widgets = {
            'facility': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select '}),
            'staff_type': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select '}),
            'first_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'First Name', }),
            'last_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Last Name', }),
            'phone': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'image': forms.ClearableFileInput()

        }


class UpdateSelfForm(forms.ModelForm):
    class Meta:
        model = StaffModel
        fields = ['phone', 'image']

        widgets = {
            'phone': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'image': forms.ClearableFileInput()

        }