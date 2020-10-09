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
       :setting:`MIDDLEWARE`. It must be installed *after*
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

    MIDDLEWARE = [
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django_otp.middleware.OTPMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ]

The plugins contain models that must be migrated.


.. _upgrading:

Upgrading
---------

Version 0.2.4 of django-otp introduced a South migration to the otp_totp plugin.
Version 0.3.0 added Django 1.7 and South migrations to all apps. Care must be
taken when upgrading in certain cases.

The recommended procedure is:

    1. Upgrade django-otp to 0.2.7, as described below.
    2. Upgrade Django to 1.7 or later.
    3. Upgrade django-otp to the latest version.

django-otp 0.4 dropped support for Django < 1.7.


Upgrading from 0.2.3 or Earlier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're using django-otp <= 0.2.3, you need to convert otp_totp to South
before going any further::

    pip install 'django-otp==0.2.7'
    python manage.py migrate otp_totp 0001 --fake
    python manage.py migrate otp_totp

If you're not using South, you can run ``python manage.py sql otp_totp`` to see
the definition of the new ``last_t`` field and then construct a suitable ``ALTER
TABLE`` SQL statement for your database.


Upgrading to Django 1.7+
~~~~~~~~~~~~~~~~~~~~~~~~

Once you've upgraded django-otp to version 0.2.4 or later (up to 0.2.7), it's
safe to switch to Django 1.7 or later. You should not have South installed at
this point, so any old migrations will simply be ignored.

Once on Django 1.7+, it's safe to upgrade django-otp to 0.3 or later. All
plugins with models have Django migrations, which will be ignored if the tables
have already been created.

If you're already on django-otp 0.3 or later when you move to Django 1.7+ (see
below), you'll want to make sure Django knows that all migrations have already
been run::

    python manage.py migrate --fake <otp_plugin>
    ...


Upgrading to 0.3.x with South
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to upgrade django-otp to 0.3.x under South, you'll need to convert
all of the remaining plugins. First make sure you're running South 1.0, as
earlier versions will not find the migrations. Then convert any plugin that you
have installed::

    pip install 'django-otp>=0.3'
    python manage.py migrate otp_hotp 0001 --fake
    python manage.py migrate otp_static 0001 --fake
    python manage.py migrate otp_yubikey 0001 --fake
    python manage.py migrate otp_twilio 0001 --fake


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
For example, you might have a `YubiKey`_ that supports both the Yubico OTP
algorithm and the HOTP standard: these would be represented as different devices
and likely served by different plugins. A device that delivered HOTP values to a
user by SMS would be a third device defined by another plugin.

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


.. _YubiKey: http://www.yubico.com/yubikey


.. _built-in-plugins:

Built-in Plugins
~~~~~~~~~~~~~~~~

django-otp includes support for several standard device types.
:class:`~django_otp.plugins.otp_hotp.models.HOTPDevice` and
:class:`~django_otp.plugins.otp_totp.models.TOTPDevice` handle standard OTP
algorithms, which can be used with a variety of OTP generators. For example,
it's easy to pair these devices with `Google Authenticator`_ using the `otpauth
URL scheme`_. If you have the `qrcode`_ package installed, the admin interface
will generate QR Codes for you.


.. _Google Authenticator: https://github.com/google/google-authenticator
.. _otpauth URL scheme: https://github.com/google/google-authenticator/wiki/Key-Uri-Format
.. _qrcode: https://pypi.python.org/pypi/qrcode/


.. _hotp-devices:

HOTP Devices
++++++++++++

`HOTP`_ is an algorithm that generates a pseudo-random sequence of codes based
on an incrementing counter. Every time a prover generates a new code or a
verifier verifies one, they increment their respective counters. This algorithm
will fail if the prover generates too many codes without a successful
verification.

If there is a failed attempt, this plugin will enforce an exponentially
increasing delay before allowing verification to succeed (see
:setting:`OTP_HOTP_THROTTLE_FACTOR`). The
:meth:`~django_otp.models.Device.verify_token` method automatically applies this
policy. For a better user experience, before calling
:meth:`~django_otp.models.Device.verify_token` check whether verification is
disabled by calling the :meth:`~django_otp.models.Device.verify_is_allowed`
method.

.. module:: django_otp.plugins.otp_hotp

.. automodule:: django_otp.plugins.otp_hotp.models
    :members:

.. autoclass:: django_otp.plugins.otp_hotp.admin.HOTPDeviceAdmin

.. _HOTP: http://tools.ietf.org/html/rfc4226#section-5

HOTP Settings
'''''''''''''

.. setting:: OTP_HOTP_ISSUER

**OTP_HOTP_ISSUER**

Default: ``None``

The ``issuer`` parameter for the otpauth URL generated by
:attr:`~django_otp.plugins.otp_hotp.models.HOTPDevice.config_url`.
This can be a string or a callable to dynamically set the value.


.. setting:: OTP_HOTP_THROTTLE_FACTOR

**OTP_HOTP_THROTTLE_FACTOR**

Default: ``1``

This controls the rate of throttling. The sequence of 1, 2, 4, 8... seconds is
multiplied by this factor to define the delay imposed after 1, 2, 3, 4...
successive failures. Set to ``0`` to disable throttling completely.


.. _totp-devices:

TOTP Devices
++++++++++++

`TOTP`_ is an algorithm that generates a pseudo-random sequence of codes based
on the current time. A typical implementation will change codes every 30
seconds, although this is configurable. This algorithm will fail if the prover
and verifier have clocks that drift too far apart.

If there is a failed attempt, this plugin will enforce an exponentially
increasing delay before allowing verification to succeed (see
:setting:`OTP_TOTP_THROTTLE_FACTOR`). The
:meth:`~django_otp.models.Device.verify_token` method automatically applies this
policy. For a better user experience, before calling
:meth:`~django_otp.models.Device.verify_token` check whether verification is
disabled by calling the :meth:`~django_otp.models.Device.verify_is_allowed`
method.

.. module:: django_otp.plugins.otp_totp

.. automodule:: django_otp.plugins.otp_totp.models
    :members:

.. autoclass:: django_otp.plugins.otp_totp.admin.TOTPDeviceAdmin

.. _TOTP: http://tools.ietf.org/html/rfc6238#section-4

TOTP Settings
'''''''''''''

.. setting:: OTP_TOTP_ISSUER

**OTP_TOTP_ISSUER**

Default: ``None``

The ``issuer`` parameter for the otpauth URL generated by
:attr:`~django_otp.plugins.otp_totp.models.TOTPDevice.config_url`.
This can be a string or a callable to dynamically set the value.

.. setting:: OTP_TOTP_SYNC

**OTP_TOTP_SYNC**

Default: ``True``

If true, then TOTP devices will keep track of the difference between the
prover's clock and our own. Any time a
:class:`~django_otp.plugins.otp_totp.models.TOTPDevice` matches a token in the
past or future, it will update
:attr:`~django_otp.plugins.otp_totp.models.TOTPDevice.drift` to the number of
time steps that the two sides are out of sync. For subsequent tokens, we'll
slide the window of acceptable tokens by this number.


.. setting:: OTP_TOTP_THROTTLE_FACTOR

**OTP_TOTP_THROTTLE_FACTOR**

Default: ``1``

This controls the rate of throttling. The sequence of 1, 2, 4, 8... seconds is
multiplied by this factor to define the delay imposed after 1, 2, 3, 4...
successive failures. Set to ``0`` to disable throttling completely.


Static Devices
++++++++++++++

.. module:: django_otp.plugins.otp_static

.. automodule:: django_otp.plugins.otp_static.models
    :members: StaticDevice, StaticToken

.. autoclass:: django_otp.plugins.otp_static.admin.StaticDeviceAdmin

Static Settings
'''''''''''''''
.. setting:: OTP_STATIC_THROTTLE_FACTOR

**OTP_STATIC_THROTTLE_FACTOR**

Default: ``1``

This controls the rate of throttling. The sequence of 1, 2, 4, 8… seconds is
multiplied by this factor to define the delay imposed after 1, 2, 3, 4…
successive failures. Set to 0 to disable throttling completely.

.. _addstatictoken:

addstatictoken
''''''''''''''

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

Email Settings
''''''''''''''

.. setting:: OTP_EMAIL_SENDER

**OTP_EMAIL_SENDER**

Default: ``None``

The email address to use as the sender when we deliver tokens. If not set, this
will automatically use :setting:`DEFAULT_FROM_EMAIL`.


.. setting:: OTP_EMAIL_SUBJECT

**OTP_EMAIL_SUBJECT**

Default: ``'OTP token'``

The subject of the email. You probably want to customize this.


.. setting:: OTP_EMAIL_TOKEN_TEMPLATE

**OTP_EMAIL_BODY_TEMPLATE**

Default: ``None``

A raw template string to use for the email body. The render context will
include the generated token in the ``token`` key.

If this and :setting:`OTP_EMAIL_BODY_TEMPLATE_PATH<OTP_EMAIL_TOKEN_TEMPLATE_PATH>`
are not set, we'll render the template 'otp/email/token.txt', which you'll most
likely want to override.

.. setting:: OTP_EMAIL_TOKEN_TEMPLATE_PATH

**OTP_EMAIL_BODY_TEMPLATE_PATH**

Default: ``otp/email/token.txt``

A path string to a template file to use for the email body. The render context
will include the generated token in the ``token`` key.

If this and :setting:`OTP_EMAIL_BODY_TEMPLATE<OTP_EMAIL_TOKEN_TEMPLATE>` are not
set, we'll render the template 'otp/email/token.txt', which you'll most likely
want to override.

.. setting:: OTP_EMAIL_TOKEN_VALIDITY

**OTP_EMAIL_TOKEN_VALIDITY**

Default: ``300``

The maximum number of seconds a token is valid.


.. setting:: OTP_EMAIL_THROTTLE_FACTOR

**OTP_EMAIL_THROTTLE_FACTOR**

Default: ``1``

This controls the rate of throttling. The sequence of 1, 2, 4, 8… seconds is
multiplied by this factor to define the delay imposed after 1, 2, 3, 4…
successive failures. Set to 0 to disable throttling completely.



.. _other-plugins:

Other Plugins
~~~~~~~~~~~~~~

The framework author also maintains a couple of other plugins for less common
devices. Third-party plugins are not listed here.

    - `django-otp-yubikey`_ supports YubiKey USB devices.
    - `django-otp-twilio`_ supports delivering tokens via Twilio's SMS service.


Settings
--------

.. setting:: OTP_LOGIN_URL

**OTP_LOGIN_URL**

Default: alias for :setting:`LOGIN_URL`

The URL where requests are redirected for two-factor authentication, especially
when using the :func:`~django_otp.decorators.otp_required` decorator.


.. setting:: OTP_ADMIN_HIDE_SENSITIVE_DATA

**OTP_ADMIN_HIDE_SENSITIVE_DATA**

Default: `False`

This controls showing some sensitive data on the Django admin site (e.g., keys
and corresponding QR codes, static tokens). Note, it is respected by built-in
plugins, but external ones may or may not support it.


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
   `django-agent-trust`_ and `django-otp-agents`_. The former deals with
   assigning trust to user agents (i.e. browsers) across sessions and the latter
   includes tools to use OTPs to establish that trust.


.. _django-agent-trust: http://pypi.python.org/pypi/django-agent-trust
.. _django-otp-agents: http://pypi.python.org/pypi/django-otp-agents
.. _django-otp-yubikey: https://django-otp-yubikey.readthedocs.io
.. _django-otp-twilio: https://django-otp-twilio.readthedocs.io
