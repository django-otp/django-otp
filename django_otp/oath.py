from hashlib import sha1
import hmac
from struct import pack
from time import time

from django.utils import six

if six.PY3:
    iterbytes = iter
else:
    iterbytes = lambda buf: (ord(b) for b in buf)


def hotp(key, counter, digits=6):
    """
    Implementation of the HOTP algorithm from `RFC 4226
    <http://tools.ietf.org/html/rfc4226#section-5>`_.

    :param bytes key: The shared secret. A 20-byte string is recommended.
    :param int counter: The password counter.
    :param int digits: The number of decimal digits to generate.

    :returns: The HOTP token.
    :rtype: int

    >>> key = b'12345678901234567890'
    >>> for c in range(10):
    ...     hotp(key, c)
    755224
    287082
    359152
    969429
    338314
    254676
    287922
    162583
    399871
    520489
    """
    msg = pack('>Q', counter)
    hs = hmac.new(key, msg, sha1).digest()
    hs = list(iterbytes(hs))

    offset = hs[19] & 0x0f
    bin_code = (hs[offset] & 0x7f) << 24 | hs[offset + 1] << 16 | hs[offset + 2] << 8 | hs[offset + 3]
    hotp = bin_code % pow(10, digits)

    return hotp


def totp(key, step=30, t0=0, digits=6, drift=0):
    """
    Implementation of the TOTP algorithm from `RFC 6238
    <http://tools.ietf.org/html/rfc6238#section-4>`_.

    :param bytes key: The shared secret. A 20-byte string is recommended.
    :param int step: The time step in seconds. The time-based code changes
        every ``step`` seconds.
    :param int t0: The Unix time at which to start counting time steps.
    :param int digits: The number of decimal digits to generate.
    :param int drift: The number of time steps to add or remove. Delays and
        clock differences might mean that you have to look back or forward a
        step or two in order to match a token.

    :returns: The TOTP token.
    :rtype: int

    >>> key = b'12345678901234567890'
    >>> now = int(time())
    >>> for delta in range(0, 200, 20):
    ...     totp(key, t0=(now-delta))
    755224
    755224
    287082
    359152
    359152
    969429
    338314
    338314
    254676
    287922
    """
    t = ((int(time()) - t0) // step) + drift

    return hotp(key, t, digits=digits)
