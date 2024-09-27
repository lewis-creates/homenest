from django.contrib import admin
from .models import Contact


class ContactAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'email',
        'subject',
        'enquiry',
        'date_submitted',
    )


admin.site.register(Contact, ContactAdmin)
