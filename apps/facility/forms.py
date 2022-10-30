from django import forms
from .models import ResourceCenter


class ResourceCenterForm(forms.ModelForm):

    class Meta:
        model = ResourceCenter
        exclude = {'uploaded_by'}

        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Title', }),
            'video_id': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Video ID', 'required': 'required'}),
            'link': forms.URLInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter Link', 'required': 'required'}),
            'doc': forms.ClearableFileInput(
                attrs={'required': 'required'}
            )
        }