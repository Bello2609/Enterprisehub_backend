from django import forms
from .models import Credit


class CreditMemberForm(forms.ModelForm):

    class Meta:
        model = Credit
        fields = ['member', 'amount', 'payment_mode']

        widgets = {
            'member': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select '}),
            'amount': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Amount'}),
            'payment_mode': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select '}),
        }
