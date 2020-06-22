import django.conf


class Settings:
    """
    This is a simple class to take the place of the global settings object. An
    instance will contain all of our settings as attributes, with default values
    if they are not specified by the configuration.
    """
    defaults = {
        'OTP_LOGIN_URL': django.conf.settings.LOGIN_URL,
        'OTP_ADMIN_HIDE_SENSITIVE_DATA': False,
    }

    def __init__(self):
        """
        Loads our settings from django.conf.settings, applying defaults for any
        that are omitted.
        """
        for name, default in self.defaults.items():
            value = getattr(django.conf.settings, name, default)
            setattr(self, name, value)


settings = Settings()
