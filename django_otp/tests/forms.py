from django.test import TestCase
from django.core import mail

from django_otp.forms import OTPAuthenticationForm
from django_otp.plugins.otp_static.models import StaticDevice
from django_otp.plugins.otp_email.models import EmailDevice


class AuthFormTest(TestCase):
    fixtures = ['tests/alice_and_bob.yaml']

    def test_empty(self):
        data = {}
        form = OTPAuthenticationForm(None, data)

        self.assert_(not form.is_valid())
        self.assertEqual(form.get_user(), None)

    def test_bad_password(self):
        data = {
            'username': 'alice',
            'password': 'bogus',
        }
        form = OTPAuthenticationForm(None, data)

        self.assert_(not form.is_valid())
        self.assert_(form.get_user() is None)
        self.assertEqual(form.errors.keys(), ['__all__'])

    def test_no_token(self):
        data = {
            'username': 'alice',
            'password': 'password',
        }
        form = OTPAuthenticationForm(None, data)

        self.assert_(not form.is_valid())
        self.assert_(form.get_user().username == 'alice')

    def test_passive_token(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_token': 'alice1',
        }
        form = OTPAuthenticationForm(None, data)

        self.assert_(form.is_valid())
        alice = form.get_user()
        self.assert_(alice.username == 'alice')
        self.assert_(isinstance(alice.otp_device, StaticDevice))
        self.assertEqual(alice.otp_device.token_set.count(), 2)

    def test_spoofed_device(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_device': 'django_otp.plugins.otp_static.models.StaticDevice/10',
            'otp_token': 'bob1',
        }
        form = OTPAuthenticationForm(None, data)

        self.assert_(not form.is_valid())
        alice = form.get_user()
        self.assert_(alice.username == 'alice')
        self.assert_(alice.otp_device is None)

    def test_specific_device_fail(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_device': 'django_otp.plugins.otp_email.models.EmailDevice/1',
            'otp_token': 'alice1',
        }
        form = OTPAuthenticationForm(None, data)

        self.assert_(not form.is_valid())
        alice = form.get_user()
        self.assert_(alice.username == 'alice')
        self.assert_(alice.otp_device is None)

    def test_specific_device(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_device': 'django_otp.plugins.otp_static.models.StaticDevice/1',
            'otp_token': 'alice1',
        }
        form = OTPAuthenticationForm(None, data)

        self.assert_(form.is_valid())
        alice = form.get_user()
        self.assert_(alice.username == 'alice')
        self.assert_(alice.otp_device is not None)

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
        self.assert_(alice.username == 'alice')
        self.assert_(alice.otp_device is None)
        self.assertEqual(len(mail.outbox), 1)

        data['otp_token'] = mail.outbox[0].body
        del data['otp_challenge']
        form = OTPAuthenticationForm(None, data)

        self.assert_(form.is_valid())
        self.assert_(isinstance(form.get_user().otp_device, EmailDevice))
