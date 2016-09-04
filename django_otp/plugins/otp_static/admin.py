from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from .models import StaticDevice, StaticToken


class StaticTokenInline(admin.TabularInline):
    model = StaticToken
    extra = 0


class StaticDeviceAdmin(admin.ModelAdmin):
    """
    :class:`~django.contrib.admin.ModelAdmin` for
    :class:`~django_otp.plugins.otp_static.models.StaticDevice`.
    """
    fieldsets = [
        ('Identity', {
            'fields': ['user', 'name', 'confirmed'],
        }),
    ]
    raw_id_fields = ['user']

    inlines = [
        StaticTokenInline,
    ]


# Somehow this is getting imported twice, triggering a useless exception.
try:
    admin.site.register(StaticDevice, StaticDeviceAdmin)
except AlreadyRegistered:
    pass
