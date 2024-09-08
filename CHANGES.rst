v1.5.4 - September 06, 2024 - Ignore proxy models when enumerating device classes
--------------------------------------------------------------------------------

- `#161`_: Discard proxied models when iterating device models

.. _#161: https://github.com/django-otp/django-otp/pull/161


v1.5.3 - September 04, 2024 - Small admin template fix
--------------------------------------------------------------------------------

- `#158`_: Remove JS focus() in admin login template

.. _#158: https://github.com/django-otp/django-otp/pull/158


v1.5.2 - August 18, 2024 - otp_verification_failed signal
--------------------------------------------------------------------------------

- `#150`_: Add signal when OTP verification fails

.. _#150: https://github.com/django-otp/django-otp/pull/150


v1.5.1 - July 23, 2024 - Admin search fields
--------------------------------------------------------------------------------

- `#147`_: Add search ability in admin using username and email

.. _#147: https://github.com/django-otp/django-otp/pull/147


v1.5.0 - April 16, 2024 - Support segno for QR codes
--------------------------------------------------------------------------------

- `#141`_: Support alternative QR code library `segno`_.

  Previously, only the `qrcode`_ library was supported.

  Use ``segno`` by installing ``django-otp[segno]`` or just install the
  ``segno`` package.

.. _#141: https://github.com/django-otp/django-otp/issues/141
.. _segno: https://pypi.python.org/pypi/segno/


v1.4.1 - April 10, 2024 - Minor EmailDevice updates
--------------------------------------------------------------------------------

- `#140`_: Support customization of email delivery.

  See the :class:`~django_otp.plugins.otp_email.models.EmailDevice`
  documentation for API details.

- Support translation of the "sent by email" message.

.. _#140: https://github.com/django-otp/django-otp/pull/140


v1.4.0 - April 09, 2024 - Add TimestampMixin
--------------------------------------------------------------------------------

- `#137`_: Add TimestampMixin

  Add a new TimestampMixin with ``created_at`` and ``last_used_at`` fields for
  device models.

  All builtin plugins now have these timestamp fields and require migrating.

- Some documentation cleanup.

.. _#137: https://github.com/django-otp/django-otp/pull/137


v1.3.0 - November 08, 2023 - Support cooldowns for token generation
--------------------------------------------------------------------------------

- `#122`_: Added throttling to token generation.

  Devices that generate random tokens can take advantage of the new
  :class:`~django_otp.models.CooldownMixin` to enforce limits on how frequently
  new tokens can be generated (and presumably delivered).
  :class:`~django_otp.plugins.otp_email.models.EmailDevice` uses this and has a
  :setting:`default cooldown <OTP_EMAIL_COOLDOWN_DURATION>` configured.

  Thanks to `Demetris Stavrou`_ for this feature.

- Note: :class:`~django_otp.models.VerifyNotAllowed` is now an
  :class:`~enum.Enum`. This will break any code that inadvisably hard-coded the
  string value of the `N_FAILED_ATTEMPTS` property.

.. _#122: https://github.com/django-otp/django-otp/pull/122
.. _Demetris Stavrou: https://github.com/demestav


v1.2.4 - October 05, 2023 - Portuguese translation
--------------------------------------------------------------------------------

- `#133`_: Add pt-PT translation.

.. _#133: https://github.com/django-otp/django-otp/pull/133


v1.2.3 - September 17, 2023 - German translation fix
--------------------------------------------------------------------------------

- `#131`_: Fix German translation

.. _#131: https://github.com/django-otp/django-otp/pull/131


v1.2.2 - June 16, 2023 - otp_email html support
--------------------------------------------------------------------------------

- `#125`_: Support email body_html templates

.. _#125: https://github.com/django-otp/django-otp/pull/125


v1.2.1 - May 26, 2023 - pt-BR translations
--------------------------------------------------------------------------------

- `#124`_: Add pt-BR translations.

.. _#124: https://github.com/django-otp/django-otp/pull/124


v1.2.0 - May 11, 2023 - Tooling, TOTP images
--------------------------------------------------------------------------------

- This project is now managed with `hatch`_, which replaces setuptools, pipenv,
  and tox. Users of the package should not be impacted. Developers can refer to
  the readme for details. If you're packaging this project from source, I
  suggest relying on pip's isolated builds rather than using hatch directly.

- `#123`_: Add support for passing an image parameter in the otpauth URL.
  See :setting:`OTP_TOTP_IMAGE`.


.. _hatch: https://hatch.pypa.io/
.. _#123: https://github.com/django-otp/django-otp/pull/123


v1.1.6 - March 07, 2023 - German translation
--------------------------------------------------------------------------------

- `#116`_: Add German translation

.. _#116: https://github.com/django-otp/django-otp/pull/116


v1.1.5 - March 06, 2023 - Bugfix release
--------------------------------------------------------------------------------

- `#115`_: Force OTP_EMAIL_SUBJECT to be a string

.. _#115: https://github.com/django-otp/django-otp/pull/115


v1.1.4 - November 10, 2022 - Spanish translation
--------------------------------------------------------------------------------

- `#106`_: Add Spanish translation

.. _#106: https://github.com/django-otp/django-otp/pull/106


v1.1.3 - November 30, 2021 - Admin template fix
--------------------------------------------------------------------------------

- `#89`_: Use the standard `username` context variable for compatibility.

.. _#89: https://github.com/django-otp/django-otp/pull/89


v1.1.2 - November 29, 2021 - Forward compatibility
--------------------------------------------------------------------------------

- `#93`_: Default to AutoField to avoid spurious migrations.

.. _#93: https://github.com/django-otp/django-otp/issues/93



v1.1.1 - September 14, 2021 - Throttling message fix
--------------------------------------------------------------------------------

- `#87`_: Fix ``locked_until`` key in throttling reason map.

.. _#87: https://github.com/django-otp/django-otp/issues/87


v1.1.0 - September 13, 2021 - Concurrent verification
--------------------------------------------------------------------------------

Where possible, all APIs now verify tokens atomically. This prevents race
conditions that could result in a token being verified twice as well as closing
gaps in throttling enforcement. Low-level integrators may still need to
:ref:`manage their own transactions <Low-Level API>`.


v1.0.6 - May 28, 2021 - Email customization
--------------------------------------------------------------------------------

- `#82`_: Add ability to pass extra context when rendering
  :class:`~django_otp.plugins.otp_email.models.EmailDevice` templates.

.. _#82: https://github.com/django-otp/django-otp/issues/82



v1.0.5 - May 08, 2021 - config_url fix
--------------------------------------------------------------------------------

- `#77`_: Force username to a string in `config_url`. Note that this might not
  produce a very human-friendly result, but it shouldn't throw an exception.

.. _#77: https://github.com/django-otp/django-otp/issues/77


v1.0.4 - April 28, 2021 - Dark mode fix
--------------------------------------------------------------------------------

- `#76`_: Django 3.2 supports the prefers-color-scheme media query, so we need
  to force a white background for QR codes.

.. _#76: https://github.com/django-otp/django-otp/issues/76


v1.0.3 - April 03, 2021 - Email body template path setting
--------------------------------------------------------------------------------

- `#71`_: Provide time at which throttling lock expires.

.. _#71: https://github.com/django-otp/django-otp/issues/71


v1.0.2 - October 23, 2020 - Email body template path setting
--------------------------------------------------------------------------------

- Added a setting to load the email body template from a template file.


v1.0.1 - October 06, 2020 - Add French translations
--------------------------------------------------------------------------------

- Added contributed French string translations.


v1.0.0 - August 13, 2020 - Update supported Django verisons.
--------------------------------------------------------------------------------

- Dropped support for Django < 2.2.


v0.9.4 - August 05, 2020 - Django 3.1 support
--------------------------------------------------------------------------------

- `#49`_: Hide the navigation sidebar on the login page.

.. _#49: https://github.com/django-otp/django-otp/issues/49


v0.9.3 - June 23, 2020 - June 18, 2020 - Admin fix
--------------------------------------------------------------------------------

- Stricter authorization checks for qrcodes in the admin interface.


v0.9.1 - May 08, 2020 - Admin fix
--------------------------------------------------------------------------------

- `#38`_: Update admin fields for
  :class:`~django_otp.plugins.otp_email.models.EmailDevice`.

.. _#38: https://github.com/django-otp/django-otp/pull/38


v0.9.0 - April 17, 2020 - Improved email device
--------------------------------------------------------------------------------

:class:`~django_otp.models.SideChannelDevice` is a new abstract device class to
simplify writing devices that deliver tokens to the user by other channels
(email, SMS, etc.).

- `#33`_, `#34`_ (`arjan-s`_): Implement
  :class:`~django_otp.models.SideChannelDevice`, reimplement
  :class:`~django_otp.plugins.otp_email.models.EmailDevice` on top of it, and
  add a few settings for customization.

- Add rate limiting to
  :class:`~django_otp.plugins.otp_email.models.EmailDevice` and
  :class:`~django_otp.plugins.otp_static.models.StaticDevice`.


.. _#33: https://github.com/django-otp/django-otp/pull/33
.. _#34: https://github.com/django-otp/django-otp/pull/34
.. _arjan-s: https://github.com/arjan-s


v0.8.1 - February 08, 2020 - Admin fix
--------------------------------------------------------------------------------

- `#26`_: Display OTP Token field on the login page even when user has not yet
  authenticated.

.. _#26: https://github.com/django-otp/django-otp/issues/26


v0.8.0 - February 06, 2020 - Drop Python 2 support
--------------------------------------------------------------------------------

- `#17`_: Drop Python 2 support.

- `#18`_: Back to a single login template for now.

- `#23`_: Allow :setting:`OTP_HOTP_ISSUER` and :setting:`OTP_TOTP_ISSUER` to be
  callable.

.. _#17: https://github.com/django-otp/django-otp/pull/17
.. _#18: https://github.com/django-otp/django-otp/pull/18
.. _#23: https://github.com/django-otp/django-otp/pull/23


v0.7.5 - December 27, 2019 - Django 3.0 support
--------------------------------------------------------------------------------

- `#15`_: Add admin template for Django 3.0.

.. _#15: https://github.com/django-otp/django-otp/issues/15


v0.7.4 - November 21, 2019 - Cleanup
--------------------------------------------------------------------------------

- `#10`_: Remove old admin login templates that are confusing some unrelated
  tools.

.. _#10: https://github.com/django-otp/django-otp/issues/10


v0.7.3 - October 22, 2019 - Minor improvements
----------------------------------------------

- Built-in forms have autocomplete disabled for token widgets.

- Fixed miscellaneous typos.


v0.7.2 - September 17, 2019 - LoginView fix
-------------------------------------------

- `#2`_: Fix LoginView for already-authenticated users, with multiple auth
  backends configured.

.. _#2: https://github.com/django-otp/django-otp/issues/2


v0.7.1 - September 12, 2019 - Preliminary Django 3.0 support
------------------------------------------------------------

Removed dependencies on Python 2 compatibility shims in Django < 3.0.


v0.7.0 - August 26, 2019 - Housekeeping
---------------------------------------

Removed obsolete compatibility shims. The testing and support matrix is
unchanged from 0.6.0, so there should be no impact.


v0.6.0 - April 22, 2019 - Failure throttling
--------------------------------------------

- Built-in :ref:`HOTP <hotp-devices>` and :ref:`TOTP <totp-devices>` devices are
  now rate-limited, enforcing exponentially increasing delays between successive
  failures. See the device documentation for information on presenting more
  useful error messages when this happens, as well as for tuning (or disabling)
  this behavior.

  Thanks to Luke Plant for the idea and implementation.


v0.5.2 - February 11 - 2019 - Fix URL encoding
----------------------------------------------

- Fix encoding of otpauth:// URL parameters.


v0.5.1 - October 24, 2018 - Customizable error messages
-------------------------------------------------------

- Error messages in :class:`~django_otp.forms.OTPAuthenticationForm` and
  :class:`~django_otp.forms.OTPTokenForm` can be customized.


v0.5.0 - August 14, 2018 - Django 2.1 support
---------------------------------------------

- Remove dependencies on old non-class login views.

- Drop support for Django < 1.11.


v0.4.3 - March 8, 2018 - Minor static token fix
-----------------------------------------------

- Fix return type of
  :meth:`~django_otp.plugins.otp_static.models.StaticToken.random_token`.


v0.4.2 - December 15, 2017 - addstatictoken fix
-----------------------------------------------

- Fix addstatictoken string handling under Python 3.


v0.4.1 - August 29, 2017 - Misc fixes
-------------------------------------

- Improved handling of device persistent identifiers.

- Make sure default keys are unicode values.


v0.4.0 - July 19, 2017 - Update support matrix
----------------------------------------------

- Fix addstatictoken on Django 1.10+.

- Drop support for versions of Django that are past EOL.


v0.3.14 - May 30, 2017 - addstatictoken fix
-------------------------------------------

- Update addstatictoken command for current Django versions.


v0.3.13 - April 11, 2017 - Pickle compatibility
-----------------------------------------------

- Allow verified users to be pickled.


v0.3.12 - April 2, 2017 - Forward compatibility
-----------------------------------------------

- Minor fixes for Django 1.11 and 2.0.


v0.3.11 - March 8, 2017 - Built-in QR Code support
--------------------------------------------------

- Generate HOTP and TOTP otpauth URLs and corresponding QR Codes. To enable this
  feature, install ``django-otp[qrcode]`` or just install the `qrcode`_ package.

- Support for Python 2.6 and Django 1.4 were dropped in this version (long
  overdue).

.. _qrcode: https://pypi.python.org/pypi/qrcode/


v0.3.8 - November 27, 2016 - Forward compatbility for Django 2.0
----------------------------------------------------------------

- Treat :attr:`~django.contrib.auth.models.User.is_authenticated` and
  :attr:`~django.contrib.auth.models.User.is_anonymous` as properties in Django
  1.10 and later.

- Add explict on_delete behavior for all foreign keys.


v0.3.7 - September 24, 2016 - Convenience API
---------------------------------------------

- Added a convenience API for verifying TOTP tokens:
  :meth:`django_otp.oath.TOTP.verify`.


v0.3.6 - September 4, 2016 - Django 1.10
----------------------------------------

- Don't break the laziness of ``request.user``.

- Improved error message for invalid tokens.

- Support the new middleware API in Django 1.10.


v0.3.5 - April 13, 2016 - Fix default TOTP key
----------------------------------------------

- The default (random) key for a new TOTP device is now forced to a unicode
  string.


v0.3.4 - January 10, 2016 - Python 3 cleanup
--------------------------------------------

- All modules include all four Python 3 __future__ imports for consistency.

- Migrations no longer have byte strings in them.


v0.3.3 - October 15, 2015 - Django 1.9
--------------------------------------

- Fix the addstatictoken management command under Django 1.9.


v0.3.2 - October 11, 2015 - Django 1.8
--------------------------------------

- Stop importing models into the root of the package.

- Use ModelAdmin.raw_id_fields for foreign keys to users.

- General cleanup and compatibility with Django 1.9a1.


v0.3.1 - April 3, 2015 - Django 1.8
-----------------------------------

- Add support for the new app registry, when available.

- Add Django 1.8 to the test matrix and fix a few test bugs.


v0.3.0 - February 7, 2015 - Support Django migrations
-----------------------------------------------------

- All plugins now have both Django and South migrations. Please see the `upgrade
  notes`_ for details on upgrading from previous versions.

.. _upgrade notes: https://pythonhosted.org/django-otp/overview.html#upgrading


v0.2.7 - April 26, 2014 - Fix for Custom user models with South
---------------------------------------------------------------

- Updated the otp_totp South migrations to support custom user models. Thanks to
  https://bitbucket.org/robirichter.


v0.2.6 - April 18, 2014 - Fix for Python 3.2 with South
-------------------------------------------------------

- Removed South-generated unicode string literals.


v0.2.4 - April 15, 2014 - TOTP plugin fix (migration warning)
-------------------------------------------------------------

- Per the RFC, :class:`~django_otp.plugins.otp_totp.models.TOTPDevice` will no
  longer verify the same token twice.

- Cosmetic fixes to the admin login form on Django 1.6.

.. warning::

    This includes a model change in TOTPDevice. If you are upgrading and your
    project uses South, you should first convert it to South with ``manage
    migrate otp_totp 0001 --fake``. If you're not using South, you will need to
    generate and run the appropriate SQL manually.


v0.2.3 - March 3, 2014 - Fix pickling
-------------------------------------

- OTPMiddleware no longer interferes with pickling request.user.


v0.2.2 - December 31, 2013 - Require Django 1.4.2
-------------------------------------------------

- Update Django requirement to 1.4.2, the first version with django.utils.six.


v0.2.1 - November 19, 2013 - Bug fix
------------------------------------

- Fix unicode representation of devices in some exotic scenarios.


v0.2.0 - November 10, 2013 - Django 1.6
---------------------------------------

- Now supports Django 1.4 to 1.6 on Python 2.6, 2.7, 3.2, and 3.3. This is the
  first release for Python 3.


v0.1.8 - August 20, 2013 - user_has_device API
-----------------------------------------------

- Add :func:`django_otp.user_has_device` to detect whether a user has any
  devices configured. This change supports a fix in django-otp-agents 0.1.4.


v0.1.7 - July 3, 2013 - Decorator improvement
-----------------------------------------------

- Add if_configured argument to :func:`~django_otp.decorators.otp_required`.


v0.1.6 - May 9, 2013 - Unit test improvements
---------------------------------------------

- Major unit test cleanup. Tests should pass or be skipped under all supported
  versions of Django, with or without custom users and timzeone support.


v0.1.5 - May 8, 2013 - OTPAdminSite improvement
-----------------------------------------------

- OTPAdminSite now selects an apporpriate login template automatically, based on
  the current Django version. Django versions 1.3 to 1.5 are currently
  supported.

- Unit test cleanup.


v0.1.3 - March 10, 2013 - Django 1.5 compatibility
--------------------------------------------------

- Add support for custom user models in Django 1.5.

- Stop using ``Device.objects``: Django doesn't allow access to an abstract
  model's manager any more.


v0.1.2 - October 8, 2012 - Bug fix
----------------------------------

- Fix an exception when an empty login form is submitted.


v0.1.0 - August 20, 2012 - Initial Release
------------------------------------------

Initial release.
