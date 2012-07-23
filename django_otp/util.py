from binascii import hexlify, unhexlify
from random import randrange

from django.core.exceptions import ValidationError


def hex_validator(length=0):
    """
    Returns a function to be used as a model validator for a hex-encoded
    CharField. This is useful for secret keys of all kinds::

        key = models.CharField(max_length=40, validators=[hex_validator(20)], help_text=u'A hex-encoded 20-byte secret key')

    :param int length: If greater than 0, validation will fail unless the
        decoded value is exactly this number of bytes.

    :rtype: function

    >>> hex_validator()('0123456789abcdef')
    >>> hex_validator(8)('0123456789abcdef')
    >>> hex_validator()('blarg')
    Traceback (most recent call last):
        ...
    ValidationError: [u'blarg is not valid hex-encoded data.']
    >>> hex_validator(9)('0123456789abcdef')
    Traceback (most recent call last):
        ...
    ValidationError: [u'0123456789abcdef does not represent exactly 9 bytes.']
    """
    def _validator(value):
        try:
            unhexlify(value)
        except StandardError:
            raise ValidationError(u'{0} is not valid hex-encoded data.'.format(value))

        if (length > 0) and (len(value) != length * 2):
            raise ValidationError(u'{0} does not represent exactly {1} bytes.'.format(value, length))

    return _validator


def random_hex(length=20):
    """
    Returns a string of random bytes encoded as hex. This is useful for secret
    keys.

    :param int length: The number of (decoded) bytes to return.

    :returns: A string of hex digits.
    :rtype: str
    """
    data = ''.join(chr(randrange(256)) for i in xrange(length))

    return hexlify(data)
