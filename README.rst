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

* Repository: https://bitbucket.org/psagers/django-otp
* Documentation: https://django-otp-official.readthedocs.io/
* Mailing list: https://groups.google.com/forum/#!forum/django-otp

This version is supported on Python 2.7 and 3.4+; and Django 1.8 and 1.10+.

.. _upgrade notes: https://pythonhosted.org/django-otp/overview.html#upgrading

.. vim:ft=rst
