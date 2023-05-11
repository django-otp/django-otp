Authentication and Authorization
================================

This section describes the process for verifying users against their registered
OTP devices as well as limiting access based on this verification.


Authenticating Users
--------------------

Soliciting an OTP token from a user is more complicated than soliciting a
password. For one thing, each user may have any number of OTP devices registered
to their account and the token itself won't tell us which one is intended. And,
of course, we won't even know which devices we should check until after we've
identified the user based on their username and password. Complicating this
further is the fact some plugins are interactive, in which case verifying the
user is at least a two-step process.

Verifying a user can happen in one or two stages. One option is to require an
OTP up front along with a password. Alternatively, we can accept single-factor
authentication initially, but allow (or require) the user to provide a second
factor later on. The following sections begin with the simpler strategies and
proceed to the lower-level APIs that will allow you to implement more complex
policies.


The Easy Way
~~~~~~~~~~~~

.. autoclass:: django_otp.views.LoginView


The Authentication Form
~~~~~~~~~~~~~~~~~~~~~~~

Django provides some high-level APIs to make it easy to authenticate users. If
you're accustomed to using Django's built-in login view, this section will show
you how to turn it into a two-factor login view.

In Django, user authentication actually takes place not in a view, but in an
:class:`~django.contrib.auth.forms.AuthenticationForm` or a subclass. If you're
using Django's :class:`built-in login view
<django.contrib.auth.views.LoginView>`, you're already using the default
AuthenticationForm. This form performs authentication as part of its
validation; validation only succeeds if the supplied credentials pass
:func:`django.contrib.auth.authenticate`.

If you want to require two-factor authentication in the default login view, the
easiest way is to use :class:`django_otp.forms.OTPAuthenticationForm` instead.
This form includes additional fields and behavior to solicit an OTP token from
the user and verify it against their registered devices. This form's validation
only succeeds if it is able to both authenticate the user with the username and
password and also verify them with an OTP token. The form can be used with
:class:`django.contrib.auth.views.LoginView` simply by passing it in the
``authentication_form`` keyword parameter::

    from django.contrib.auth.views import LoginView
    from django_otp.forms import OTPAuthenticationForm

    urlpatterns = [
        url(r'^accounts/login/$', LoginView.as_view(authentication_form=OTPAuthenticationForm)),
    )

.. autoclass:: django_otp.forms.OTPAuthenticationForm

Following is a sample template snippet that's designed for
:class:`~django_otp.forms.OTPAuthenticationForm`:

.. code-block:: html

    <form action="." method="POST">
        <div class="form-row"> {{ form.username.errors }}{{ form.username.label_tag }}{{ form.username }} </div>
        <div class="form-row"> {{ form.password.errors }}{{ form.password.label_tag }}{{ form.password }} </div>
        {% if form.get_user %}
        <div class="form-row"> {{ form.otp_device.errors }}{{ form.otp_device.label_tag }}{{ form.otp_device }} </div>
        {% endif %}
        <div class="form-row"> {{ form.otp_token.errors }}{{ form.otp_token.label_tag }}{{ form.otp_token }} </div>
        <div class="submit-row">
            <input type="submit" value="Log in"/>
            {% if form.get_user %}<input type="submit" name="otp_challenge" value="Get Challenge" />{% endif %}
        </div>
    </form>


The Admin Site
~~~~~~~~~~~~~~

In addition to providing :class:`~django_otp.forms.OTPAuthenticationForm` for
your normal login views, django-otp includes an
:class:`~django.contrib.admin.AdminSite` subclass for admin integration.

.. autoclass:: django_otp.admin.OTPAdminSite
    :members: name, login_form, login_template, has_permission

.. autoclass:: django_otp.admin.OTPAdminAuthenticationForm

Django has a mechanism for :ref:`overriding-default-admin-site`.

.. note::

    If you switch to OTPAdminSite before setting up your first device,
    you'll find yourself with a bit of a chicken-egg problem. Remember that you
    can always use the :ref:`addstatictoken` management command to bootstrap
    yourself in.

As a convenience, :class:`~django_otp.admin.OTPAdminSite` will override the
admin login template. The template is a bit of a moving target, so this may get
broken by new Django versions. Users will probably have a better and more
consistent experience if you send them through your own login UI instead.


The Token Form
~~~~~~~~~~~~~~

If you already have an authenticated user and you just want to ask for an OTP
token to verify, you can use :class:`django_otp.forms.OTPTokenForm`.

.. autoclass:: django_otp.forms.OTPTokenForm


Custom Forms
~~~~~~~~~~~~

Most of the functionality of :class:`~django_otp.forms.OTPAuthenticationForm`
and :class:`~django_otp.forms.OTPTokenForm` is implemented in a mixin class:

.. autoclass:: django_otp.forms.OTPAuthenticationFormMixin


.. _Low-Level API:

The Low-Level API
~~~~~~~~~~~~~~~~~

More customized integrations can use these APIs to manage the verification
process directly.

.. warning::

   Verifying OTP tokens should always take place inside of a transaction. If
   you're loading the devices yourself, be sure to use
   :meth:`~django.db.models.query.QuerySet.select_for_update` to prevent
   concurrent access. Relevant APIs below have a ``for_verify`` parameter for
   this purpose.

.. autofunction:: django_otp.devices_for_user

.. autofunction:: django_otp.user_has_device

.. autofunction:: django_otp.verify_token

.. autofunction:: django_otp.match_token

.. autofunction:: django_otp.login

.. autoclass:: django_otp.models.Device
    :members: is_interactive, generate_challenge, verify_token, verify_is_allowed, persistent_id, from_persistent_id

.. autoclass:: django_otp.models.DeviceManager
    :members: devices_for_user

.. autoclass:: django_otp.models.VerifyNotAllowed


Authorizing Users
-----------------

If you design your site to always require OTP verification in order to log in,
then your authorization policies don't need to change.
``request.user.is_authenticated()`` will be effectively synonymous with
``request.user.is_verified()``. If, on the other hand, you anticipate having
both verified and unverified users on your site, you're probably intending to
limit access to some resources to verified users only. The primary tool for this
is otp_required:

.. decorator:: django_otp.decorators.otp_required([redirect_field_name='next', login_url=None, if_configured=False])

    Similar to :func:`~django.contrib.auth.decorators.login_required`, but
    requires the user to be :term:`verified`. By default, this redirects users
    to :setting:`OTP_LOGIN_URL`.

    :param if_configured: If ``True``, an authenticated user with no confirmed
        OTP devices will be allowed. Default is ``False``.
    :type if_configured: bool

If you need more fine-grained control over authorization decisions, you can use
``request.user.is_verified()`` to determine whether the user has been verified
by an OTP device. if ``is_verified()`` is true, then ``request.user.otp_device``
will be set to the :class:`~django_otp.models.Device` object that verified the
user. This can be useful if you want to include the name of the verifying device
in the UI.

If you want to use OTPs to establish trusted user agents (e.g. a browser that
the user claims is on a private and secure computer), look at
`django-agent-trust <http://pypi.python.org/pypi/django-agent-trust>`_ and
`django-otp-agents <http://pypi.python.org/pypi/django-otp-agents>`_.


.. _Managing Devices:

Managing Devices
----------------

django-otp does not include any standard mechanism for managing a user's devices
outside of the admin interface. All plugins are expected to include admin
integration, which should be sufficient for many sites. Some sites may want to
provide users a self-service API to manage devices, but this will be very
site-specific. Fortunately, managing a user's devices is just a matter of
managing :class:`~django_otp.models.Device`-derived model objects, so it will be
easy to implement. Be sure to note the :ref:`warning <unsaved_device_warning>`
about unsaved :class:`~django_otp.models.Device` objects.
