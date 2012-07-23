from random import choice

from django.db import models

from django_otp.models import Device


class StaticDevice(Device):
    """
    A static device simply consists of random tokens shared by the database and
    the user. These are frequently used as emergency tokens in case a user's
    normal device is lost or unavailable. They can be consumed in any order;
    each token will be removed from the database as soon as it is used.

    This model has no fields of its own, but serves as a container for
    :class:`StaticToken` objects.
    """
    def verify_token(self, token):
        try:
            match = self.token_set.filter(token=token).iterator().next()
            match.delete()
        except StopIteration:
            match = None

        return (match is not None)

    @staticmethod
    def random_token():
        """
        Returns a new random static token.

        :rtype: str
        """
        return ''.join(choice('abcdefghjkmnpqrstuvwxyz') for i in xrange(16))


class StaticToken(models.Model):
    """
    A single token belonging to a :class:`StaticDevice`.

    .. attribute:: device

        A foreign key to :class:`StaticDevice`.

    .. attribute:: token

        A random string up to 16 characters.
    """
    device = models.ForeignKey(StaticDevice, related_name='token_set')
    token = models.CharField(max_length=16, db_index=True)
