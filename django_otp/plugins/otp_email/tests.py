from django.db import IntegrityError
from django.core import mail

from django_otp.forms import OTPAuthenticationForm
from django_otp.tests import TestCase
from .models import EmailDevice


class AuthFormTest(TestCase):
    def setUp(self):
        try:
            alice = self.create_user('alice', 'password')
        except IntegrityError:
            self.skipTest(u"Failed to create user.")
        else:
            alice.emaildevice_set.create()

        if not hasattr(alice, 'email'):
            self.skipTest(u"User model has no email.")

    def test_email_interaction(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_device': 'django_otp.plugins.otp_email.models.EmailDevice/1',
            'otp_token': '',
            'otp_challenge': '1',
        }
        form = OTPAuthenticationForm(None, data)

        self.assert_(not form.is_valid())
        alice = form.get_user()
        self.assert_(alice.get_username() == 'alice')
        self.assert_(alice.otp_device is None)
        self.assertEqual(len(mail.outbox), 1)

        data['otp_token'] = mail.outbox[0].body
        del data['otp_challenge']
        form = OTPAuthenticationForm(None, data)

        self.assert_(form.is_valid())
        self.assert_(isinstance(form.get_user().otp_device, EmailDevice))
