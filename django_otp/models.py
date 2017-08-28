from __future__ import absolute_import, division, print_function, unicode_literals

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import six


class DeviceManager(models.Manager):
    """
    The :class:`~django.db.models.Manager` object installed as
    ``Device.objects``.
    """
    def devices_for_user(self, user, confirmed=None):
        """
        Returns a queryset for all devices of this class that belong to the
        given user.

        :param user: The user.
        :type user: :class:`~django.contrib.auth.models.User`

        :param confirmed: If ``None``, all matching devices are returned.
            Otherwise, this can be any true or false value to limit the query
            to confirmed or unconfirmed devices, respectively.
        """
        devices = self.model.objects.filter(user=user)
        if confirmed is not None:
            devices = devices.filter(confirmed=bool(confirmed))

        return devices


class Device(models.Model):
    """
    Abstract base model for a :term:`device` attached to a user. Plugins must
    subclass this to define their OTP models.

    .. _unsaved_device_warning:

    .. warning::

        OTP devices are inherently stateful. For example, verifying a token is
        logically a mutating operation on the device, which may involve
        incrementing a counter or otherwise consuming a token. A device must be
        committed to the database before it can be used in any way.

    .. attribute:: user

        *ForeignKey*: Foreign key to your user model, as configured by
        :setting:`AUTH_USER_MODEL` (:class:`~django.contrib.auth.models.User`
        by default).

    .. attribute:: name

        *CharField*: A human-readable name to help the user identify their
        devices.

    .. attribute:: confirmed

        *BooleanField*: A boolean value that tells us whether this device has
        been confirmed as valid. It defaults to ``True``, but subclasses or
        individual deployments can force it to ``False`` if they wish to create
        a device and then ask the user for confirmation. As a rule, built-in
        APIs that enumerate devices will only include those that are confirmed.

    .. attribute:: objects

        A :class:`~django_otp.models.DeviceManager`.
    """
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), help_text="The user that this device belongs to.", on_delete=models.CASCADE)
    name = models.CharField(max_length=64, help_text="The human-readable name of this device.")
    confirmed = models.BooleanField(default=True, help_text="Is this device ready for use?")

    objects = DeviceManager()

    class Meta(object):
        abstract = True

    def __str__(self):
        if six.PY3:
            return self.__unicode__()
        else:
            return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        try:
            user = self.user
        except ObjectDoesNotExist:
            user = None

        return "{0} ({1})".format(self.name, user)

    @property
    def persistent_id(self):
        return '{0}/{1}'.format(self.model_label(), self.id)

    @classmethod
    def model_label(cls):
        """
        Returns an identifier for this Django model class.

        This is just the standard "<app_label>.<model_name>" form.

        """
        return '{0}.{1}'.format(cls._meta.app_label, cls._meta.model_name)

    @classmethod
    def from_persistent_id(cls, persistent_id):
        """
        Loads a device from its persistent id::

            device == Device.from_persistent_id(device.persistent_id)

        """
        device = None

        try:
            model_label, device_id = persistent_id.rsplit('/', 1)
            app_label, model_name = model_label.split('.')

            device_cls = apps.get_model(app_label, model_name)
            if issubclass(device_cls, Device):
                device = device_cls.objects.filter(id=int(device_id)).first()
        except (ValueError, LookupError):
            pass

        return device

    def is_interactive(self):
        """
        Returns ``True`` if this is an interactive device. The default
        implementation returns ``True`` if
        :meth:`~django_otp.models.Device.generate_challenge` has been
        overridden, but subclasses are welcome to provide smarter
        implementations.

        :rtype: bool
        """
        return not hasattr(self.generate_challenge, 'stub')

    def generate_challenge(self):
        """
        Generates a challenge value that the user will need to produce a token.
        This method is permitted to have side effects, such as transmitting
        information to the user through some other channel (email or SMS,
        perhaps). And, of course, some devices may need to commit the
        challenge to the databse.

        :returns: A message to the user. This should be a string that fits
            comfortably in the template ``'OTP Challenge: {0}'``. This may
            return ``None`` if this device is not interactive.
        :rtype: string or ``None``

        :raises: Any :exc:`~exceptions.Exception` is permitted. Callers should
            trap ``Exception`` and report it to the user.
        """
        return None
    generate_challenge.stub = True

    def verify_token(self, token):
        """
        Verifies a token. As a rule, the token should no longer be valid if
        this returns ``True``.

        :param string token: The OTP token provided by the user.
        :rtype: bool
        """
        return False
