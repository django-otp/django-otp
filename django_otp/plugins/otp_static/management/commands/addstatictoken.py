from __future__ import absolute_import, division, print_function, unicode_literals

from optparse import make_option
from textwrap import fill

from django.core.management.base import BaseCommand, CommandError

from django_otp.plugins.otp_static.lib import get_user_model, add_static_token


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
            statictoken = add_static_token(username, options.get('token'))
        except get_user_model().DoesNotExist:
            raise CommandError('User "{0}" does not exist.'.format(username))

        self.stdout.write(statictoken.token)
