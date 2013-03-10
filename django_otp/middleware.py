from . import DEVICE_ID_SESSION_KEY
from .models import Device


class OTPMiddleware(object):
    """
    This must be installed after
    :class:`~django.contrib.auth.middleware.AuthenticationMiddleware` and
    performs an analagous function. Just as AuthenticationMiddleware populates
    ``request.user`` based on session data, OTPMiddleware populates
    ``request.user.otp_device`` to the :class:`~django_otp.models.Device`
    object that has verified the user, or ``None`` if the user has not been
    verified.  As a convenience, this also installs ``user.is_verified()``,
    which returns ``True`` if ``user.otp_device`` is not ``None``.
    """
    def process_request(self, request):
        user = getattr(request, 'user', None)

        if user is None:
            return None

        user.otp_device = None
        user.is_verified = lambda: user.otp_device is not None

        if user.is_anonymous():
            return None

        device_id = request.session.get(DEVICE_ID_SESSION_KEY)
        device = Device.from_persistent_id(device_id) if device_id else None

        if (device is not None) and (device.user_id != user.id):
            device = None

        if (device is None) and (DEVICE_ID_SESSION_KEY in request.session):
            del request.session[DEVICE_ID_SESSION_KEY]

        user.otp_device = device

        return None
