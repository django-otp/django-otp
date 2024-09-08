from django_otp.plugins.otp_totp.models import TOTPDevice


class TOTPDeviceProxy(TOTPDevice):
    class Meta:
        proxy = True
