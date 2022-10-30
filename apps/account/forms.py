from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django import forms
from django.forms.widgets import PasswordInput, EmailInput


class ChangePasswordForm(PasswordChangeForm):
    """
       Change Password Form
    """
    old_password = forms.CharField(widget=PasswordInput(attrs={'name': 'old_password',
                                                               'class': 'form-control input-height col-md-3',
                                                               'type': 'password','id': 'old_password',
                                                               'placeholder': 'Old Password'}))
    new_password1 = forms.CharField(widget=PasswordInput(attrs={'name': 'password1',
                                                                'class': 'form-control input-height col-md-3',
                                                                'type': 'password', 'id': 'new-password1',
                                                                'placeholder': 'New Password'}))
    new_password2 = forms.CharField(widget=PasswordInput(attrs={'name': 'password2',
                                                                'class': 'form-control input-height col-md-3',
                                                                'type': 'password', 'id': 'new-password2',
                                                                'placeholder': 'Confirm Password'}))
