from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from .models import EmailDevice


class EmailDeviceAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Identity', {
            'fields': ['user', 'name', 'confirmed'],
        }),
        ('Configuration', {
            'fields': ['key'],
        }),
    ]


# Somehow this is getting imported twice, triggering a useless exception.
try:
    admin.site.register(EmailDevice)
except AlreadyRegistered:
    pass
