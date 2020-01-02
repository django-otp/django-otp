from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

from .models import TOTPDevice


class TOTPDeviceAdmin(admin.ModelAdmin):
    """
    :class:`~django.contrib.admin.ModelAdmin` for
    :class:`~django_otp.plugins.otp_totp.models.TOTPDevice`.
    """
    list_display = ['user', 'name', 'confirmed', 'qrcode_link']

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
        ('Throttling', {
            'fields': ['throttling_failure_timestamp', 'throttling_failure_count'],
        }),
        (None, {
            'fields': ['qrcode_link'],
        }),
    ]
    raw_id_fields = ['user']
    readonly_fields = ['qrcode_link']
    radio_fields = {'digits': admin.HORIZONTAL}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user')

        return queryset

    #
    # Columns
    #

    def qrcode_link(self, device):
        try:
            href = reverse('admin:otp_totp_totpdevice_config', kwargs={'pk': device.pk})
            link = format_html('<a href="{}">qrcode</a>', href)
        except Exception:
            link = ''

        return link
    qrcode_link.short_description = "QR Code"

    #
    # Custom views
    #

    def get_urls(self):
        urls = [
            url(r'^(?P<pk>\d+)/config/$', self.admin_site.admin_view(self.config_view), name='otp_totp_totpdevice_config'),
            url(r'^(?P<pk>\d+)/qrcode/$', self.admin_site.admin_view(self.qrcode_view), name='otp_totp_totpdevice_qrcode'),
        ] + super().get_urls()

        return urls

    def config_view(self, request, pk):
        device = TOTPDevice.objects.get(pk=pk)

        try:
            context = dict(
                self.admin_site.each_context(request),
                device=device,
            )
        except AttributeError:  # Older versions don't have each_context().
            context = {'device': device}

        return TemplateResponse(request, 'otp_totp/admin/config.html', context)

    def qrcode_view(self, request, pk):
        device = TOTPDevice.objects.get(pk=pk)

        try:
            import qrcode
            import qrcode.image.svg

            img = qrcode.make(device.config_url, image_factory=qrcode.image.svg.SvgImage)
            response = HttpResponse(content_type='image/svg+xml')
            img.save(response)
        except ImportError:
            response = HttpResponse('', status=503)

        return response


try:
    admin.site.register(TOTPDevice, TOTPDeviceAdmin)
except AlreadyRegistered:
    # A useless exception from a double import
    pass
