from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from .models import EmailDevice


class EmailDeviceAdmin(admin.ModelAdmin):
    pass


# Somehow this is getting imported twice, triggering a useless exception.
try:
    admin.site.register(EmailDevice)
except AlreadyRegistered:
    pass
