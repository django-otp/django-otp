import os.path

from django.core.exceptions import ImproperlyConfigured


try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def _load_config(path: str, required) -> dict:
    if os.path.exists(path):
        with open(path, 'rb') as f:
            config = tomllib.load(f)
    elif required:
        raise ImproperlyConfigured(f"{path} does not exist.")
    else:
        config = {}

    return config


def load() -> dict:
    path = os.getenv('DJANGO_OTP_CONFIG')
    env = os.getenv('HATCH_ENV_ACTIVE', '').split('.', 1)[0]

    if path:
        config = _load_config(path, required=True)
    elif env:
        config = _load_config(f'test/config/env-{env}.toml', required=False)
    else:
        config = {}

    return config
