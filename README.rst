This project makes it easy to add support for `one-time passwords
<http://en.wikipedia.org/wiki/One-time_password>`_ (OTPs) to Django. It can be
integrated at various levels, depending on how much customization is required.
It integrates with ``django.contrib.auth``, although it is not a Django
authentication backend. The primary target is developers wishing to incorporate
OTPs into their Django projects as a form of `two-factor authentication
<http://en.wikipedia.org/wiki/Two-factor_authentication>`_.

This project includes several simple OTP plugins and more are available
separately. This package also includes an implementation of OATH `HOTP
<http://tools.ietf.org/html/rfc4226>`_ and `TOTP
<http://tools.ietf.org/html/rfc6238>`_ for convenience, as these are standard
OTP algorithms used by multiple plugins.

This version is supported on Python 2.6, 2.7, and 3.3+; and Django >= 1.4.2.

.. warning::

    All plugins now contain both South and Django migrations. If you're using
    South or upgrading to Django 1.7, please see the `upgrade notes`_ in the
    documentation first.

.. _upgrade notes: https://pythonhosted.org/django-otp/overview.html#upgrading

.. vim:ft=rst
