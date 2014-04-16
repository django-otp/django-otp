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
    return TOTP(key, step, t0, digits, drift).token()


class TOTP(object):
    """
    An alternate TOTP interface.

    This provides access to intermediate steps of the computation. This is a
    living object: the return values of ``t`` and ``token`` will change along
    with other properties and with the passage of time.

    :param bytes key: The shared secret. A 20-byte string is recommended.
    :param int step: The time step in seconds. The time-based code changes
        every ``step`` seconds.
    :param int t0: The Unix time at which to start counting time steps.
    :param int digits: The number of decimal digits to generate.
    :param int drift: The number of time steps to add or remove. Delays and
        clock differences might mean that you have to look back or forward a
        step or two in order to match a token.

    >>> key = b'12345678901234567890'
    >>> totp = TOTP(key)
    >>> totp.time = 0
    >>> totp.t()
    0
    >>> totp.token()
    755224
    >>> totp.time = 30
    >>> totp.t()
    1
    >>> totp.token()
    287082
    >>> del totp.time
    >>> totp.t0 = int(time()) - 60
    >>> totp.t()
    2
    >>> totp.token()
    359152
    """
    def __init__(self, key, step=30, t0=0, digits=6, drift=0):
        self.key = key
        self.step = step
        self.t0 = t0
        self.digits = digits
        self.drift = drift
        self._time = None

    def token(self):
        """ The computed TOTP token. """
        return hotp(self.key, self.t(), digits=self.digits)

    def t(self):
        """ The computed time step. """
        return ((int(self.time) - self.t0) // self.step) + self.drift

    @property
    def time(self):
        """
        The current time.

        By default, this returns time.time() each time it is accessed. If you
        want to generate a token at a specific time, you can set this property
        to a fixed value instead. Deleting the value returns it to its 'live'
        state.

        """
        return self._time if (self._time is not None) else time()

    @time.setter
    def time(self, value):
        self._time = value

    @time.deleter
    def time(self):
        self._time = None
