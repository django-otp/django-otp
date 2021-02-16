from binascii import unhexlify
from importlib import import_module

from django.db import models
from django.utils.module_loading import import_string



class EncryptedHexCharField(models.CharField):
    """
    A CharField that stores hex strings with the ability to encrypt it as well.

    Encryption has to be configured using OTP_ENCRYPTION_OBJECT in the settings.
    The value has to point to a class or module with 'encrypt' and 'decrypt' methods.
    Both methods take a value
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        from django_otp.conf import settings
        otp_encryption_object = settings.OTP_ENCRYPTION_OBJECT
        print("otp_encryption_object: %s" % otp_encryption_object)
        try:
            # Maybe the path is to an object in a module
            encryption_object = import_string(otp_encryption_object)
        except ImportError:
            # Maybe the path is to a module itself
            encryption_object = import_module(otp_encryption_object)

        self.encrypt = getattr(encryption_object, 'encrypt')
        self.decrypt = getattr(encryption_object, 'decrypt')

    def get_db_prep_save(self, value, connection):
        if not value:
            return value
        binary = self.encrypt(unhexlify(value))
        return super().get_db_prep_value(binary.hex(), connection)

    def from_db_value(self, value, *args):
        if not value:
            return value

        binary = self.decrypt(unhexlify(value))
        return binary.hex()
