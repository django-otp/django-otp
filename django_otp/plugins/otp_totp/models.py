from binascii import unhexlify

from django.db import models

from django_otp.models import Device
from django_otp.oath import totp
from django_otp.util import random_hex, hex_validator

from .conf import settings


class TOTPDevice(Device):
    """
    A generic TOTP device. The model fields mostly correspond to the arguments
    to :func:`django_otp.oath.totp`. They all have sensible defaults, including
    the key, which is randomly generated.

    .. attribute:: key

        A hex-encoded secret key of up to 40 bytes. (Default: 20 random bytes)

    .. attribute:: step

        The time step in seconds. (Default: 30)

    .. attribute:: t0

        The Unix time at which to begin counting steps. (Default: 0)

    .. attribute:: digits

        The number of digits to expect in a token. (Default: 6)

    .. attribute:: tolerance

        The number of time steps in the past or future to allow. (Default: 1)

    .. attribute:: drift

        The number of time steps the prover is known to deviate from our clock.
        (Default: 0)
    """
    key = models.CharField(max_length=80, validators=[hex_validator()], default=lambda: random_hex(20), help_text=u"A hex-encoded secret key of up to 40 bytes.")
    step = models.PositiveSmallIntegerField(default=30, help_text=u"The time step in seconds.")
    t0 = models.BigIntegerField(default=0, help_text=u"The Unix time at which to begin counting steps.")
    digits = models.PositiveSmallIntegerField(choices=[(6,6), (8,8)], default=6, help_text=u"The number of digits to expect in a token.")
    tolerance = models.PositiveSmallIntegerField(default=1, help_text=u"The number of time steps in the past or future to allow.")
    drift = models.SmallIntegerField(default=0, help_text=u"The number of time steps the prover is known to deviate from our clock.")

    class Meta(Device.Meta):
        verbose_name = u"TOTP device"

    @property
    def bin_key(self):
        return unhexlify(self.key)

    def verify_token(self, token):
        try:
            token = int(token)
        except ValueError:
            verified = False
        else:
            key = self.bin_key

            for offset in range(-self.tolerance, self.tolerance + 1):
                if totp(key, self.step, self.t0, self.digits, self.drift + offset) == token:
                    if (offset != 0) and settings.OTP_OATH_TOTP_SYNC:
                        self.drift += offset
                        self.save()

                    verified = True
                    break
            else:
                verified = False

        return verified
