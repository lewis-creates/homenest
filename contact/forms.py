from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        # Define the model and fields for the form
        model = Contact
        fields = ['full_name', 'email', 'subject', 'enquiry']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            if field == 'enquiry':
                # Add specific CSS class for the enquiry field
                self.fields[field].widget.attrs['class'] = (
                    'extra-form-label-styling-tall'
                )
            else:
                # Add general CSS class for the rest
                self.fields[field].widget.attrs['class'] = (
                    'extra-form-label-styling'
                )