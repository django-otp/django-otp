from __future__ import print_function

from optparse import make_option
from textwrap import fill

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from django_otp.plugins.otp_static.models import StaticDevice, StaticToken


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-t', '--token', dest='token', help=u'The token to add. If omitted, one will be randomly generated.'),
    )
    args = u'<username>'
    help = fill(u'Adds a single static OTP token to the given user. ' \
        u'The token will be added to an arbitrary static device ' \
        u'attached to the user, creating one if necessary.', width=78)

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Please specify exactly one username.')

        username = args[0]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError('User "{0}" does not exist.'.format(username))

        device = next(StaticDevice.objects.filter(user=user).iterator(), None)
        if device is None:
            device = StaticDevice.objects.create(user=user, name=u'Backup Code')

        token = options.get('token')
        if token is None:
            token = StaticDevice.random_token()

        device.token_set.add(StaticToken(token=token))

        print(token, file=self.stdout)
