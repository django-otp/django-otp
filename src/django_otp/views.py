from __future__ import absolute_import, division, print_function, unicode_literals

from functools import partial

from django.contrib.auth import views as auth_views
from django.utils.functional import cached_property

from django_otp import _user_is_anonymous
from django_otp.forms import OTPAuthenticationForm, OTPTokenForm


class LoginView(auth_views.LoginView):
    """
    This is a replacement for :class:`django.contrib.auth.views.LoginView` that
    requires two-factor authentication. It's slightly clever: if the user is
    already authenticated but not verified, it will only ask the user for their
    OTP token. If the user is anonymous or is already verified by an OTP
    device, it will use the full username/password/token form. In order to use
    this, you must supply a template that is compatible with both
    :class:`~django_otp.forms.OTPAuthenticationForm` and
    :class:`~django_otp.forms.OTPTokenForm`. This is a good view for
    :setting:`OTP_LOGIN_URL`.

    """
    otp_authentication_form = OTPAuthenticationForm
    otp_token_form = OTPTokenForm

    @cached_property
    def authentication_form(self):
        user = self.request.user
        if _user_is_anonymous(user) or user.is_verified():
            form = self.otp_authentication_form
        else:
            form = partial(self.otp_token_form, user)

        return form


# Backwards compatibility.
login = LoginView.as_view()
