from django import forms
from .models import MainSite, Portfolio
from ckeditor.fields import RichTextFormField


class WebSpaceForm(forms.ModelForm):

    class Meta:
        model = MainSite
        fields = ['url_identifier', 'about_us', 'facebook', 'instagram',
                  'google_plus', 'linkedin', 'image', ]

        widgets = {
            'url_identifier': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Unique username to identify your business. ', 'required': "required" }),
            'about_us': RichTextFormField(),
            'facebook': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Link to your facebook business profile'}),
            'instagram': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Link to your instagram business profile'}),
            'google_plus': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Link to your g-plus business profile'}),
            'linkedin': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Link to your linkedin business profilek'}),
            'image': forms.ClearableFileInput(),
        }
    #
    # def clean(self):
    #     cleaned_data = super(WebSpaceForm, self).clean()
    #
    #     identifier = cleaned_data.get('url_identifier')
    #
    #     if MainSite.objects.filter(url_identifier__exact=identifier).exists():
    #         msg = 'Sorry, the Web Space Identifier is too similar to someone else, please kindly change.'
    #         self.add_error('url_identifier', msg)
    #
    #     return cleaned_data


class EditWebSpaceForm(forms.ModelForm):

    class Meta:
        model = MainSite
        fields = ['about_us', 'facebook', 'instagram',
                  'google_plus', 'linkedin', 'image', ]

        widgets = {
            'about_us': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Talk to us about your business in 100 Words or less'}),
            'facebook': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Link to your facebook business profile'}),
            'instagram': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Link to your instagram business profile'}),
            'google_plus': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Link to your g-plus business profile'}),
            'linkedin': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Link to your linkedin business profilek'}),
            'image': forms.ClearableFileInput(),
        }


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['title', 'image', 'client', 'desc',]

        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Portfolio Title *', }),
            'client': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Service Name * ', }),
            'desc': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Describe Project ', }),
            'image': forms.ClearableFileInput()
        }

    def clean(self):
        cleaned_data = super(PortfolioForm, self).clean()
        get_member_id = cleaned_data.get('member_id')
        if Portfolio.objects.filter(member_id=get_member_id).count() >= 9:
            raise forms.ValidationError('Sorry, you cannot add more than 9 items to your portfolio')
        return cleaned_data
