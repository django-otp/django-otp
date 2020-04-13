Extending Django-OTP
====================

A django-otp plugin is defined as a Django app that includes at least one model
derived from :class:`django_otp.models.Device`. All Device-derived model objects
will be detected by the framework and included in the standard forms and APIs.


Writing a Device
----------------

A :class:`~django_otp.models.Device` subclass is only required to implement one
method:

.. automethod:: django_otp.models.Device.verify_token
    :noindex:

Most devices will also need to define one or more model fields to do anything
interesting. Here's a simple implementation of a generic TOTP device::

    from binascii import unhexlify

    from django.db import models

    from django_otp.models import Device
    from django_otp.oath import totp
    from django_otp.util import random_hex, hex_validator


    class TOTPDevice(Device):
        key = models.CharField(max_length=80,
                               validators=[hex_validator()],
                               default=lambda: random_hex(20),
                               help_text='A hex-encoded secret key of up to 40 bytes.')

        @property
        def bin_key(self):
            return unhexlify(self.key)

        def verify_token(self, token):
            """
            Try to verify ``token`` against the current and previous TOTP value.
            """
            try:
                token = int(token)
            except ValueError:
                verified = False
            else:
                verified = any(totp(self.bin_key, drift=drift) == token for drift in [0, -1])

            return verified


This example also shows some of the :ref:`low-level utilities <utilities>`
django_otp provides for OATH and hex-encoded values.

If a device uses a challenge-response algorithm or requires some other kind of
user interaction, it should implement an additional method:

.. automethod:: django_otp.models.Device.generate_challenge
    :noindex:

For devices that send a token via a separate channel, like the
:class:`~django_otp.plugins.otp_email.models.EmailDevice` example, a generic
:class:`~django_otp.models.SideChannelDevice` is provided. This abstract subclass of
:class:`~django_otp.models.Device` provides
:meth:`~django_otp.models.SideChannelDevice.generate_token` and implements
:meth:`~django_otp.models.SideChannelDevice.verify_token` for concrete devices, which
then only have to implement :meth:`~django_otp.models.Device.generate_challenge` to
actually deliver the token to the user.


.. _utilities:

Utilities
---------

django_otp provides several low-level utilities as a convenience to plugin
implementors.

django_otp.oath
~~~~~~~~~~~~~~~

.. module:: django_otp.oath
.. autofunction:: hotp
.. autofunction:: totp
.. autoclass:: TOTP
    :members:


django_otp.util
~~~~~~~~~~~~~~~

.. automodule:: django_otp.util
    :members:
