from django.conf import settings
from django.db import models


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
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), help_text=u"The user that this device belongs to.")
    name = models.CharField(max_length=64, help_text=u"The human-readable name of this device.")
    confirmed = models.BooleanField(default=True, help_text=u"Is this device ready for use?")

    objects = DeviceManager()

    class Meta(object):
        abstract = True

    def __unicode__(self):
        return u'{0}: {1}'.format(self.user.username, self.name)

    @property
    def persistent_id(self):
        return '{0}/{1}'.format(self.import_path, self.id)

    @property
    def import_path(self):
        return '{0}.{1}'.format(self.__module__, self.__class__.__name__)

    @classmethod
    def from_persistent_id(cls, path):
        """
        Loads a device from its persistent id::

            device == Device.from_persistent_id(device.persistent_id)
        """
        from . import import_class

        try:
            device_type, device_id = path.rsplit('/', 1)

            device_cls = import_class(device_type)
            device = device_cls.objects.get(id=device_id)
        except Exception:
            device = None

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
        Verifies a token. In some cases, the token will no longer be valid if
        this returns ``True``.

        .. warning::

            This method is allowed to call ``self.save()`` any time it wants.
            Some devices will update themselves on every successful
            verification. To be safe, this method should only be called on
            objects that have already been committed to the database.

        :param string token: The OTP token provided by the user.
        :rtype: bool
        """
        return False
