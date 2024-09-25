from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Placeholder dictionary
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County',
        }

        # Add placeholders, classes, and invisible labels
        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field_name, field in self.fields.items():
            if field_name != 'country':
                placeholder_text = placeholders.get(field_name, '')
                if field.required:
                    placeholder_text += ' *'
                field.widget.attrs.update({
                    'placeholder': placeholder_text,
                    'class': 'stripe-style-input',
                    'aria-label': placeholders.get(field_name, ''),
                })
            else:
                # For the country field, you should also add an aria-label
                field.widget.attrs.update({
                    'class': 'extra-form-label-styling',
                    'aria-label': 'Country'
                })