from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    # Set image field attributes
    image = forms.ImageField(label='Image', required=False,
                             widget=CustomClearableFileInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Assign friendly names of all categories to the select input
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names

        for field in self.fields:
            # Apply custom styling to the description field
            if field == 'description':
                self.fields[field].widget.attrs['class'] = (
                    'extra-form-label-styling-tall')
            # Apply general styling to other fields
            else:
                self.fields[field].widget.attrs['class'] = (
                    'extra-form-label-styling')