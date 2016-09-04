from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from .models import HOTPDevice


class HOTPDeviceAdmin(admin.ModelAdmin):
    """
    :class:`~django.contrib.admin.ModelAdmin` for
    :class:`~django_otp.plugins.otp_hotp.models.HOTPDevice`.
    """
    fieldsets = [
        ('Identity', {
            'fields': ['user', 'name', 'confirmed'],
        }),
        ('Configuration', {
            'fields': ['key', 'digits', 'tolerance'],
        }),
        ('State', {
            'fields': ['counter'],
        }),
    ]
    raw_id_fields = ['user']
    radio_fields = {'digits': admin.HORIZONTAL}


try:
    admin.site.register(HOTPDevice, HOTPDeviceAdmin)
except AlreadyRegistered:
    # A useless exception from a double import
    pass
