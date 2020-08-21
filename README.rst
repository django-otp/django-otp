django-otp
==========

.. image:: https://img.shields.io/pypi/v/django-otp?color=blue
   :target: https://pypi.org/project/django-otp/
   :alt: PyPI
.. image:: https://img.shields.io/readthedocs/django-otp-official
   :target: https://django-otp-official.readthedocs.io/
   :alt: Documentation
.. image:: https://img.shields.io/badge/github-django--otp-green
   :target: https://github.com/django-otp/django-otp
   :alt: Source

This project makes it easy to add support for `one-time passwords
<http://en.wikipedia.org/wiki/One-time_password>`_ (OTPs) to Django. It can be
integrated at various levels, depending on how much customization is required.
It integrates with ``django.contrib.auth``, although it is not a Django
authentication backend. The primary target is developers wishing to incorporate
OTPs into their Django projects as a form of `two-factor authentication
<http://en.wikipedia.org/wiki/Two-factor_authentication>`_.

Several simple OTP plugins are included and more are available separately. This
package also includes an implementation of OATH `HOTP
<http://tools.ietf.org/html/rfc4226>`_ and `TOTP
<http://tools.ietf.org/html/rfc6238>`_ for convenience, as these are standard
OTP algorithms used by multiple plugins.

If you're looking for a higher-level or more opinionated solution, you might be
interested in `django-two-factor-auth
<https://github.com/Bouke/django-two-factor-auth>`_.

Status
------

This project is stable and maintained, but is no longer actively used by the
author and is not seeing much ongoing investment. Anyone interested in taking
over aspects of the project should `contact me <https://github.com/psagers>`_.

.. end-of-doc-intro

Well-formed issues and pull requests are welcome, but please see the
:ref:`contributing` section first.


Development
-----------

Development dependencies are defined in the Pipfile; use `pipenv`_ to set up a
suitable shell.

The tests in tox.ini cover a representative sample of supported Python and
Django versions, as well as running `flake8`_ and `isort`_ for linting and style
consistency. Please run `tox` before checking in and sending a pull request.


.. _contributing:

Contributing
------------

As mentioned above, this project is stable and mature. Issues and pull requests
are welcome for important bugs and improvements. For non-trivial changes, it's
often a good idea to start by opening an issue to track the need for a change
and then optionally open a pull request with a proposed resolution. Issues and
pull requests should also be focused on a single thing. Pull requests that
bundle together a bunch of loosely related commits are unlikely to go anywhere.

Another good rule of thumb—for any project, but especially a mature one—is to
keep changes as simple as possible. In particular, there should be a high bar
for adding new dependencies. Although it can't be ruled out, it seems highly
unlikely that a new runtime dependecy will ever be added. New testing
dependencies are more likely, but only if there's no other way to address an
important need.

If there's a development tool that you'd like to use with this project, the
first step is to try to update config files (setup.cfg or similar) to integrate
the tool with the existing code. A bit of configuration glue for popular tools
should always be safe. If that's not possible, we can consider modifying the
code to be compatible with a broader range of tools (without breaking any
existing compatibilities). Only as a last resort would a new testing or
development tool be incorporated into the project as a dependency.


.. _pipenv: https://pipenv.readthedocs.io/en/latest/
.. _flake8: https://pypi.org/project/flake8/
.. _isort: https://pypi.org/project/isort/
