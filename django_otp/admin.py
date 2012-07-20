from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.admin.sites import AdminSite

from .forms import OTPAuthenticationFormMixin


class OTPAdminAuthenticationForm(AdminAuthenticationForm, OTPAuthenticationFormMixin):
    """
    An :class:`~django.contrib.admin.forms.AdminAuthenticationForm` subclass
    that solicits an OTP token. This has the same behavior as
    :class:`~django_otp.forms.OTPAuthenticationForm`.
    """
    otp_device = forms.CharField(required=False, widget=forms.Select)
    otp_token = forms.CharField(required=False)

    # This is a placeholder field that allows us to detect when the user clicks
    # the otp_challenge submit button.
    otp_challenge = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(OTPAdminAuthenticationForm, self).__init__(*args, **kwargs)

        # A litle extra cheese to make it prettier.
        self.fields['otp_token'].widget.attrs['style'] = 'width: 14em;'

    def clean(self):
        self.cleaned_data = super(OTPAdminAuthenticationForm, self).clean()
        self.clean_otp(self.get_user())

        return self.cleaned_data


class OTPAdminSite(AdminSite):
    """
    This is an :class:`~django.contrib.admin.AdminSite` subclass that requires
    two-factor authentication. Only users that can be verified by a registered
    OTP device will be authorized for this admin site. Unverified users will be
    treated as if :attr:`~django.contrib.auth.models.User.is_staff` is
    ``False``.
    """
    login_form = OTPAdminAuthenticationForm

    #: This is a modified Django 1.3 admin login template that includes our OTP
    #: fields. Feel free to override this with your own.
    login_template = 'otp/admin/login.html'

    def has_permission(self, request):
        """
        In addition to the default requirements, this only allows access to
        users who have been verified by a registered OTP device.
        """
        return super(OTPAdminSite, self).has_permission(request) and request.user.is_verified()
