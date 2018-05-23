from __future__ import absolute_import, division, print_function, unicode_literals

from base64 import b32encode
from os import urandom

from django.db import models

from django_otp.models import Device


class StaticDevice(Device):
    """
    A static :class:`~django_otp.models.Device` simply consists of random
    tokens shared by the database and the user. These are frequently used as
    emergency tokens in case a user's normal device is lost or unavailable.
    They can be consumed in any order; each token will be removed from the
    database as soon as it is used.

    This model has no fields of its own, but serves as a container for
    :class:`StaticToken` objects.

    .. attribute:: token_set

        The RelatedManager for our tokens.
    """
    def verify_token(self, token):
        try:
            match = next(self.token_set.filter(token=token).iterator())
            match.delete()
        except StopIteration:
            match = None

        return (match is not None)


class StaticToken(models.Model):
    """
    A single token belonging to a :class:`StaticDevice`.

    .. attribute:: device

        *ForeignKey*: A foreign key to :class:`StaticDevice`.

    .. attribute:: token

        *CharField*: A random string up to 16 characters.
    """
    device = models.ForeignKey(StaticDevice, related_name='token_set', on_delete=models.CASCADE)
    token = models.CharField(max_length=16, db_index=True)

    @staticmethod
    def random_token():
        """
        Returns a new random string that can be used as a static token.

        :rtype: bytes

        """
        return b32encode(urandom(5)).decode('utf-8').lower()
