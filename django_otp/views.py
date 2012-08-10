from functools import partial

from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth.views import login as auth_login

from .forms import OTPAuthenticationForm, OTPTokenForm


def login(request, **kwargs):
    """
    This is a replacement for :func:`django.contrib.auth.views.login` that
    requires two-factor authentication. It's slightly clever: if the user is
    already authenticated but not verified, it will only ask the user for their
    OTP token. If the user is anonymous or is already verified by an OTP
    device, it will use the full username/password/token form. In order to use
    this, you must supply a template that is compatible with both
    :class:`~django_otp.forms.OTPAuthenticationForm` and
    :class:`~django_otp.forms.OTPTokenForm`. This is a good view for
    :setting:`OTP_LOGIN_URL`.

    Parameters are the same as :func:`~django.contrib.auth.views.login` except
    that this view always overrides ``authentication_form``.
    """
    user = request.user

    if user.is_anonymous() or user.is_verified():
        form = OTPAuthenticationForm
    else:
        form = partial(OTPTokenForm, user)

        # A minor hack to make django.contrib.auth.login happy
        user.backend = request.session[BACKEND_SESSION_KEY]

    kwargs['authentication_form'] = form

    return auth_login(request, **kwargs)
