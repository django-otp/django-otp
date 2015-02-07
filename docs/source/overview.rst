Overview and Key Concepts
=========================

The django_otp package contains a framework for processing one-time passwords as
well as support for :ref:`several types <built-in-plugins>` of OTP devices.
Support for additional devices is handled by plugins, :ref:`distributed
separately <other-plugins>`.

Adding two-factor authentication to your Django site involves four main tasks:

    #. Installing the django-otp plugins you want to use.

    #. Adding one or more OTP-enabled login views.

    #. Restricting access to all or portions of your site based on whether users
       have been verified by a registered OTP device.

    #. Providing mechanisms to register OTP devices to user accounts (or
       relying on the Django admin interface).


.. _installation:

Installation
------------

Basic installation has only two steps:

    #. Install :mod:`django_otp` and any :ref:`plugins <built-in-plugins>` that
       you'd like to use. These are simply Django apps to be installed in the
       usual way.

    #. Add :class:`django_otp.middleware.OTPMiddleware` to
       :setting:`MIDDLEWARE_CLASSES`. It must be installed *after*
       :class:`~django.contrib.auth.middleware.AuthenticationMiddleware`.

For example::

    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
        'django.contrib.admindocs',

        'django_otp',
        'django_otp.plugins.otp_totp',
        'django_otp.plugins.otp_hotp',
        'django_otp.plugins.otp_static',
    ]

    MIDDLEWARE_CLASSES = [
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django_otp.middleware.OTPMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ]

The plugins contain models that must be migrated.


Authentication and Verification
-------------------------------

In a normal Django deployment, the user associated with a request is either
authenticated or not. With the introduction of two-factor authentication, the
situation becomes a little more complicated: while it is certainly possible to
design a site such that two factors are required for any authentication, that's
only one option. It's entirely reasonable to allow users to log in with either
one or two factors and grant then access accordingly.

In this documentation, a user that has passed Django's authentication API is
called :term:`authenticated`. A user that has additionally been accepted by a
registered OTP device is called :term:`verified`. On an OTP-enabled Django site,
there are thus three levels of authentication:

    - anonymous
    - authenticated
    - authenticated + verified

When planning your site, you'll want to consider whether different views will
require different levels of authentication. As a convenience, we provide the
decorator :func:`django_otp.decorators.otp_required`, which is analogous to
:func:`~django.contrib.auth.decorators.login_required`, but requires the user to
be both authenticated and verified.

:class:`~django_otp.middleware.OTPMiddleware` populates
``request.user.otp_device`` to the OTP device object that verified the current
user (if any). As a convenience, it also adds ``user.is_verified()`` as a
counterpart to ``user.is_authenticated()``. It is not possible for a user to be
verified without also being authenticated. [#agents]_


Plugins and Devices
-------------------

A django-otp plugin is simply a Django app that contains one or more models that
are subclassed from :class:`django_otp.models.Device`. Each model class supports
a single type of OTP device. Remember that when we use the term :term:`device`
in this context, we're not necessarily referring to a physical device. At the
code level, a device is a model object that can verify a particular type of OTP.
For example, you might have a `YubiKey <http://www.yubico.com/yubikey>`_ that
supports both the Yubico OTP algorithm and the HOTP standard: these would be
represented as different devices and likely served by different plugins. A
device that delivered HOTP values to a user by SMS would be a third device
defined by another plugin.

OTP plugins are distributed as Django apps; to install a plugin, just add it to
:setting:`INSTALLED_APPS` like any other. The order can be significant: any time
we enumerate a user's devices, such as when we ask the user which device they
would like to authenticate with, we will present them according to the order in
which the apps are installed.

OTP devices come in two general flavors: passive and interactive. A passive
device is one that can accept a token from the user and verify it with no
preparation. Examples include devices corresponding to dedicated hardware or
smartphone apps that generate sequenced or time-based tokens. An interactive
device needs to communicate something to the user before it can accept a token.
Two common types are devices that use a challenge-response OTP algorithm and
devices that deliver a token to the user through an independent channel, such as
SMS.

Internally, device instances can be flagged as confirmed or unconfirmed. By
default, devices are confirmed as soon as they are created, but a plugin or
deployment that wishes to include a confirmation step can mark a device
unconfirmed initially. Unconfirmed devices will be ignored by the high-level OTP
APIs.


.. _built-in-plugins:

Built-in Plugins
~~~~~~~~~~~~~~~~

django-otp includes support for several standard device types.
:class:`~django_otp.plugins.otp_hotp.models.HOTPDevice` and
:class:`~django_otp.plugins.otp_totp.models.TOTPDevice` handle standard OTP
algorithms, which can be used with a variety of OTP generators. For example,
it's easy to pair these devices with `Google Authenticator
<http://code.google.com/p/google-authenticator/>`_ using the `otpauth URL scheme
<http://code.google.com/p/google-authenticator/wiki/KeyUriFormat>`_.


HOTP Devices
++++++++++++

`HOTP <http://tools.ietf.org/html/rfc4226#section-5>`_ is an algorithm that
generates a pseudo-random sequence of codes based on an incrementing counter.
Every time a prover generates a new code or a verifier verifies one, they
increment their respective counters. This algorithm will fail if the prover
generates too many codes without a successful verification.

.. module:: django_otp.plugins.otp_hotp

.. automodule:: django_otp.plugins.otp_hotp.models
    :members:

.. autoclass:: django_otp.plugins.otp_hotp.admin.HOTPDeviceAdmin


TOTP Devices
++++++++++++

`TOTP <http://tools.ietf.org/html/rfc6238#section-4>`_ is an algorithm that
generates a pseudo-random sequence of codes based on the current time. A typical
implementation will change codes every 30 seconds, although this is
configurable. This algorithm will fail if the prover and verifier have clocks
that drift too far apart.

.. module:: django_otp.plugins.otp_totp

.. automodule:: django_otp.plugins.otp_totp.models
    :members:

.. autoclass:: django_otp.plugins.otp_totp.admin.TOTPDeviceAdmin

TOTP Settings
'''''''''''''

**OTP_TOTP_SYNC**

.. setting:: OTP_TOTP_SYNC

Default: ``True``

If true, then TOTP devices will keep track of the difference between the
prover's clock and our own. Any time a
:class:`~django_otp.plugins.otp_totp.models.TOTPDevice` matches a token in the
past or future, it will update
:attr:`~django_otp.plugins.otp_totp.models.TOTPDevice.drift` to the number of
time steps that the two sides are out of sync. For subsequent tokens, we'll
slide the window of acceptable tokens by this number.


Static Devices
++++++++++++++

.. module:: django_otp.plugins.otp_static

.. automodule:: django_otp.plugins.otp_static.models

    :members: StaticDevice, StaticToken

.. autoclass:: django_otp.plugins.otp_static.admin.StaticDeviceAdmin

The static plugin also includes a management command called ``addstatictoken``,
which will add a single static token to any account. This is useful for
bootstrapping and emergency access. Run ``manage.py addstatictoken -h`` for
details.


Email Devices
+++++++++++++

.. module:: django_otp.plugins.otp_email

.. automodule:: django_otp.plugins.otp_email.models
    :members: EmailDevice

.. autoclass:: django_otp.plugins.otp_email.admin.EmailDeviceAdmin


.. _other-plugins:

Other Plugins
~~~~~~~~~~~~~~

The framework author also maintains a couple of other plugins for less common
devices. Third-party plugins are not listed here.

    - `django-otp-yubikey <http://pypi.python.org/pypi/django-otp-yubikey>`_
      supports YubiKey USB devices.
    - `django-otp-twilio <http://pypi.python.org/pypi/django-otp-twilio>`_
      supports delivering OTPs via Twilio's SMS service.


Settings
--------

.. setting:: OTP_LOGIN_URL

**OTP_LOGIN_URL**

Default: alias for :setting:`LOGIN_URL`

The URL where requests are redirected for two-factor authentication, especially
when using the :func:`~django_otp.decorators.otp_required` decorator.


Glossary
--------

.. glossary::

    authenticated
        A user whose credentials have been accepted by Django's authentication
        API is considered authenticated.

    device
        A mechanism by which a user can acquire an OTP. This might correspond to
        a physical device dedicated to such a purpose, a virtual device such as
        a smart phone app, or even a set of stored single-use tokens.

    OTP
        A one-time password. This is a generated value that a user can present
        as evidence of their identity. OTPs are only valid for a single use or,
        in some cases, for a strictly limited period of time.

    prover
        An entity that is using an OTP to prove its identity. For example, a
        user who is providing an OTP token.

    token
        An encoded OTP. Some OTPs consist of structured data, in which case
        they will be encoded into a printable string for transport.

    two-factor authentication
        An authentication policy that requires a user to present two proofs of
        identity. The first is typically a password and the second is
        frequently tied to some physical device in the user's possession.

    verified
        A user whose credentials have been accepted by Django's authentication
        API and also by a registered OTP device is considered verified.

    verifier
        An entity that verifies tokens generated by a prover. For example, a web
        service that accepts OTPs as proof of identity.

----

.. rubric:: Footnotes

.. [#agents] If you'd like the second factor to persist across sessions, see
    `django-agent-trust <http://pypi.python.org/pypi/django-agent-trust>`_ and
    `django-otp-agents <http://pypi.python.org/pypi/django-otp-agents>`_. The
    former deals with assigning trust to user agents (i.e. browsers) across
    sessions and the latter includes tools to use OTPs to establish that trust.
