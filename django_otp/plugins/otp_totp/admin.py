from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from .models import TOTPDevice


class TOTPDeviceAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Identity', {
            'fields': ['user', 'name', 'confirmed'],
        }),
        ('Configuration', {
            'fields': ['key', 'step', 't0', 'digits', 'tolerance'],
        }),
        ('State', {
            'fields': ['drift'],
        }),
    ]

    radio_fields = {'digits': admin.HORIZONTAL}


try:
    admin.site.register(TOTPDevice, TOTPDeviceAdmin)
except AlreadyRegistered:
    # A useless exception from a double import
    pass
