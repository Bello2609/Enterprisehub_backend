from django import forms
from .models import Register


class ProgramRegisterForm(forms.ModelForm):

    class Meta:
        model = Register
        exclude = ['program', 'p_status', 'date']
        widgets = {

            'name': forms.TextInput(attrs={'name': 'name', 'class': 'form-control',
                                                 'placeholder': 'Enter Name', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'name': 'email', 'class': 'form-control',
                                                 'placeholder': 'Enter Email', 'required': 'required'}),
            'phone': forms.NumberInput(attrs={'name': 'phone', 'class': 'form-control',
                                                   'placeholder': 'Enter Phone Number', 'required': 'required'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control ',
                                                'placeholder': 'Your Occupation'}),
            'company': forms.TextInput(attrs={'class': 'form-control ',
                                                 'placeholder': 'Company'}),
            'designation': forms.TextInput(attrs={'class': 'form-control ',
                                                 'placeholder': 'Designation'}),
        }