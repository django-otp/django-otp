from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.auth import get_user_model

from django_otp.admin import user_model_search_fields

from .models import EmailDevice


class EmailDeviceAdmin(admin.ModelAdmin):
    """
    :class:`~django.contrib.admin.ModelAdmin` for
    :class:`~django_otp.plugins.otp_email.models.EmailDevice`.
    """

    User = get_user_model()
    candidate_search_field = [User.USERNAME_FIELD, 'email']

    list_display = ['user', 'name', 'created_at', 'last_used_at', 'confirmed']
    list_filter = ['created_at', 'last_used_at', 'confirmed']
    search_fields, search_help_text = user_model_search_fields(candidate_search_field)

    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'last_used_at']

    fieldsets = [
        (
            'Identity',
            {
                'fields': ['user', 'name', 'confirmed'],
            },
        ),
        (
            'Timestamps',
            {
                'fields': ['created_at', 'last_used_at'],
            },
        ),
        (
            'Configuration',
            {
                'fields': ['email'],
            },
        ),
    ]


# Somehow this is getting imported twice, triggering a useless exception.
try:
    admin.site.register(EmailDevice, EmailDeviceAdmin)
except AlreadyRegistered:
    pass
