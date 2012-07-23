from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from .models import StaticDevice, StaticToken


class StaticTokenInline(admin.TabularInline):
    model = StaticToken
    extra = 0


class StaticDeviceAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Identity', {
            'fields': ['user', 'name', 'confirmed'],
        }),
    ]

    inlines = [
        StaticTokenInline,
    ]


# Somehow this is getting imported twice, triggering a useless exception.
try:
    admin.site.register(StaticDevice, StaticDeviceAdmin)
except AlreadyRegistered:
    pass
