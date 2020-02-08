v0.8.1 - February 08, 2020 - Admin fix
--------------------------------------------------------------------------------

- `#26`_: Display OTP Token field on the login page even when user has not yet
  authenticated.


v0.8.0 - February 06, 2020 - Drop Python 2 support
--------------------------------------------------------------------------------

- `#17`_: Drop Python 2 support.

- `#18`_: Back to a single login template for now.

- `#23`_: Allow :setting:`OTP_HOTP_ISSUER` and :setting:`OTP_TOTP_ISSUER` to be
  callable.

.. _#17: https://github.com/django-otp/django-otp/pulls/17
.. _#18: https://github.com/django-otp/django-otp/pulls/18
.. _#23: https://github.com/django-otp/django-otp/pulls/23


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
