from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.core.mail import send_mail
from .forms import ContactForm


def contact(request):
    """
    Handles the contact form submission.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Create email subject and body with form data
            subject = "You have a new customer enquiry"
            body = {
                'full_name': form.cleaned_data['full_name'],
                'email': form.cleaned_data['email'],
                'subject': form.cleaned_data['subject'],
                'enquiry': form.cleaned_data['enquiry'],
            }
            body_string = '\n'.join(
                [f"{key}: {value}" for key, value in body.items()]
            )

            # Show success message to user
            messages.success(request, 'Thank you!'
                             ' Your enquiry has been submitted successfully!')
            # Send the email to store owner with the enquiry details
            send_mail(subject, body_string,
                      'theinhometeam@gmail.com', ['theinhometeam@gmail.com'])
            # Render the home page after successful submission
            return render(request, 'home/index.html')
        else:
            messages.error(request, 'Your submission is not valid.')
            return redirect(reverse('contact'))
    else:
        # Initialize the form with the user's email if they are logged in
        if request.user.is_authenticated:
            initial_data = {'email': request.user.email}
            form = ContactForm(initial=initial_data)
        else:
            form = ContactForm()

    # Render the contact form if the form is invalid
    return render(request, 'contact/contact.html', {'form': form})