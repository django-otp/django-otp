import sys
from itertools import ifilter

from django.contrib.auth.signals import user_logged_in
from django.db.models import get_apps, get_models

from django_otp.models import Device


DEVICE_ID_SESSION_KEY = 'otp_device_id'


def login(request, device):
    """
    Persist the given OTP device in the current session. The device will be
    rejected if it does not belong to ``request.user``.

    This is called automatically any time :func:`django.contrib.auth.login` is
    called with a user having an ``otp_device`` atribute. If you use Django's
    :func:`~django.contrib.auth.views.login` view with the django-otp
    authentication forms, then you won't need to call this.

    :param request: The HTTP request
    :type request: :class:`~django.http.HttpRequest`

    :param device: The OTP device used to verify the user.
    :type device: :class:`~django_otp.models.Device`
    """
    user = getattr(request, 'user', None)

    if (user is not None) and (device is not None) and (device.user_id == user.id):
        request.session[DEVICE_ID_SESSION_KEY] = device.persistent_id
        request.user.otp_device = device


def _handle_auth_login(sender, request, user, **kwargs):
    """
    Automatically persists an OTP device that was set by an OTP-aware
    AuthenticationForm.
    """
    if hasattr(user, 'otp_device'):
        login(request, user.otp_device)

user_logged_in.connect(_handle_auth_login)


def match_token(user, token):
    """
    Attempts to verify a :term:`token` on every device attached to the given
    user until one of them succeeds. When possible, you should prefer to verify
    tokens against specific devices.

    :param user: The user supplying the token.
    :type user: :class:`~django.contrib.auth.models.User`

    :param string token: An OTP token to verify.

    :returns: The device that accepted ``token``, if any.
    :rtype: :class:`~django_otp.models.Device` or ``None``
    """
    matches = ifilter(lambda d: d.verify_token(token), devices_for_user(user))

    return next(matches, None)


def devices_for_user(user, confirmed=True):
    """
    Returns an iterable of all devices registered to the given user.

    :param user:
    :type user: :class:`~django.contrib.auth.models.User`

    :param confirmed: If ``None``, all matching devices are returned.
        Otherwise, this can be any true or false value to limit the query
        to confirmed or unconfirmed devices, respectively.

    :rtype: iterable
    """
    for model in device_classes():
        for device in model.objects.devices_for_user(user, confirmed=confirmed):
            yield device


def device_classes():
    """
    Returns an iterable of all loaded device models.
    """
    for app in get_apps():
        for model in get_models(app):
            if issubclass(model, Device):
                yield model


def import_class(path):
    """
    Imports a class based on a full Python path ('pkg.pkg.mod.Class'). This
    does not trap any exceptions if the path is not valid.
    """
    module, name = path.rsplit('.', 1)
    __import__(module)
    mod = sys.modules[module]
    cls = getattr(mod, name)

    return cls
