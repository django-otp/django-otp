from importlib import import_module

from django.db import models
from django.utils.module_loading import import_string

from django_otp.conf import settings


class OptionalEncyptionCharField(models.CharField):
    """
    A CharField that allows encryption if so configured.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            # Maybe the path is to an object in a module
            encryption_object = import_string(settings.OTP_ENCRYPTION_OBJECT)
        except ImportError:
            # Maybe the path is to a module itself
            encryption_object = import_module(settings.OTP_ENCRYPTION_OBJECT)

        self.encrypt = getattr(encryption_object, 'encrypt')
        self.decrypt = getattr(encryption_object, 'decrypt')

    def get_db_prep_value(self, value, connection, prepared=False):
        return self.encrypt(super().get_db_prep_value(value, connection, prepared))

    def from_db_value(self, value):
        return self.to_python(super().to_python(value))

    def to_python(self, value):
        return self.decrypt(value)
