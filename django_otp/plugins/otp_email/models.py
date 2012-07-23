from binascii import unhexlify

from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string

from django_otp.models import Device
from django_otp.oath import totp
from django_otp.util import hex_validator, random_hex

from .conf import settings


class EmailDevice(Device):
    """
    An email device delivers a token to the user's registered email address
    (``user.email``). This is intended for demonstration purposes; if you allow
    users to reset their passwords via email, then this provides no security
    benefits.

    .. attribute:: key

        A hex-encoded secret key of up to 40 bytes. (Default: 20 random bytes)
    """
    key = models.CharField(max_length=80,
                           validators=[hex_validator()],
                           default=lambda: random_hex(20),
                           help_text=u'A hex-encoded secret key of up to 20 bytes.')

    @property
    def bin_key(self):
        return unhexlify(self.key)

    def generate_challenge(self):
        token = totp(self.bin_key)
        body = render_to_string('otp/email/token.txt', {'token': token})

        send_mail(settings.OTP_EMAIL_SUBJECT,
                  body,
                  settings.OTP_EMAIL_SENDER,
                  [self.user.email])

        message = u'sent by email'

        return message

    def verify_token(self, token):
        try:
            token = int(token)
        except ValueError:
            verified = False
        else:
            verified = any(totp(self.bin_key, drift=drift) == token for drift in [0, -1])

        return verified
