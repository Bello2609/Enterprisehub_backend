from django import forms
from .models import BookedServices, Services
from django.forms import formset_factory


class NewServicesForm(forms.ModelForm):

    class Meta:
        model = BookedServices
        fields = ['service', 'quantity']

        widgets = {
            'service': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select', 'required': 'required'}),
            'quantity': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': 'Quantity *',  'required': 'required' }),
        }

    def __init__(self, service_cat_id,  *args, **kwargs):
        super(NewServicesForm, self).__init__(*args, **kwargs)
        self.fields['service'].queryset = Services.objects.filter(cat_name_id=service_cat_id)


NewServiceFormSet = formset_factory(NewServicesForm)
