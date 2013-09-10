from __future__ import print_function

from optparse import make_option
from textwrap import fill

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
    get_user_model = lambda: User

from django_otp.plugins.otp_static.models import StaticDevice, StaticToken


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-t', '--token', dest='token', help='The token to add. If omitted, one will be randomly generated.'),
    )
    args = '<username>'
    help = fill('Adds a single static OTP token to the given user. '
                'The token will be added to an arbitrary static device '
                'attached to the user, creating one if necessary.', width=78)

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Please specify exactly one username.')

        username = args[0]

        try:
            user = get_user_model().objects.get_by_natural_key(username)
        except ObjectDoesNotExist:
            raise CommandError('User "{0}" does not exist.'.format(username))

        device = next(StaticDevice.objects.filter(user=user).iterator(), None)
        if device is None:
            device = StaticDevice.objects.create(user=user, name='Backup Code')

        token = options.get('token')
        if token is None:
            token = StaticToken.random_token()

        device.token_set.add(StaticToken(token=token))

        print(token, file=self.stdout)
