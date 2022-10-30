from django import forms
from .models import Bookings, HeldBookings
from ..facility.models import Category, Unit
from ..members.models import Member
from datetime import timedelta, date


class MemberBookingForm(forms.ModelForm):

    class Meta:
        model = Bookings
        fields = ['member', 'unit', 'book_from', 'facility', 'category', 'book_to']

        widgets = {

            'facility': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select'}),
            'category': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select'}),
            'unit': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select'}),
            'member': forms.Select(
                attrs={'class': 'form-control js-example-basic-select2', 'placeholder': 'Select', 'required': 'required'}),
            'book_from': forms.DateInput(attrs={'class': 'form-control input-height datepicker',
                                                'placeholder': 'Pick a date'}),
            'book_to': forms.DateInput(attrs={'class': 'form-control input-height datepicker',
                                              'placeholder': 'Pick a date'}),
        }

    def clean(self):
        cleaned_data = super(MemberBookingForm, self).clean()
        today = date.today()
        booking_date = cleaned_data.get('book_from')
        end_date = cleaned_data.get('book_to')
        unit = cleaned_data.get('unit')

        # if booking_date < today:
        #     raise forms.ValidationError({'book_from': ['Input Error...Date cannot be in the past']})

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
                            raise forms.ValidationError('Input Error. Selected dates is clashing with another booking')
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
        super(MemberBookingForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.none()
        self.fields['unit'].queryset = Unit.objects.none()
        self.fields['member'].queryset = Member.objects.filter(validated=True)

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


