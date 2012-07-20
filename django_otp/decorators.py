from django.contrib.auth.decorators import user_passes_test

from django_otp.conf import settings


def otp_required(view=None, redirect_field_name='next', login_url=None):
    """
    Similar to :func:`~django.contrib.auth.decorators.login_required`, but
    requires the user to be :term:`verified`. By default, this redirects users
    to :setting:`OTP_LOGIN_URL`.
    """
    if login_url is None:
        login_url = settings.OTP_LOGIN_URL

    decorator = user_passes_test(
        lambda u: u.is_verified(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )

    return decorator if (view is None) else decorator(view)
