from django import forms
from .models import NewPost
from ckeditor.fields import RichTextFormField


class NewPostForm(forms.ModelForm):

    class Meta:
        model = NewPost
        fields = ['category', 'title', 'content', 'image']

        widgets = {
            'category': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select '}),
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Give post a title', }),
            'content': RichTextFormField(),
            # 'publish': forms.CheckboxInput(
            #     attrs={'class': 'js-switch'}),
            'image': forms.ClearableFileInput()
        }

    def clean(self):
        cleaned_data = super(NewPostForm, self).clean()

        title = cleaned_data.get('title')

        # if NewPost.objects.filter(title__exact=title).exists():
        #     msg = 'Please change the title of this post.'
        #     self.add_error('title', msg)
        if len(title) > 254:
            msg = 'Form Error!.. Title too long'
            self.add_error('title', msg)

        return cleaned_data
