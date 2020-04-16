from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string

from django_otp.models import SideChannelDevice
from django_otp.util import hex_validator, random_hex

from .conf import settings


def default_key():
    return random_hex(20)


def key_validator(value):
    return hex_validator()(value)


class EmailDevice(SideChannelDevice):
    """
    A :class:`~django_otp.models.SideChannelDevice` that delivers a token to the email
    address saved in this object or alternatively to the user's registered email
    address (``user.email``).
    The tokens are valid for :setting:`OTP_EMAIL_TOKEN_VALIDITY` seconds.
    Once a token has been accepted, it is no longer valid

    This is intended for demonstration purposes; if you allow users to reset their
    passwords via email, then this provides no security benefits.

    .. attribute:: email

        *EmailField*: An alternative email address to send the tokens to.
    """
    email = models.EmailField(max_length=254,
                              blank=True,
                              null=True,
                              help_text='Optional alternative email address to send tokens to')

    def generate_challenge(self):
        self.generate_token(valid_secs=settings.OTP_EMAIL_TOKEN_VALIDITY)
        body = render_to_string('otp/email/token.txt', {'token': self.token})

        send_mail(settings.OTP_EMAIL_SUBJECT,
                  body,
                  settings.OTP_EMAIL_SENDER,
                  [self.email or self.user.email])

        message = "sent by email"

        return message
