from django.db import IntegrityError

from django_otp.forms import OTPAuthenticationForm
from django_otp.tests import TestCase
from .models import StaticDevice


class AuthFormTest(TestCase):
    """
    Test the auth form with static tokens.

    We try to honor custom user models, but if we can't create users, we'll
    skip the tests.
    """
    def setUp(self):
        for device_id, username in enumerate(['alice', 'bob']):
            try:
                user = self.create_user(username, 'password')
            except IntegrityError:
                self.skipTest("Unable to create a test user.")
            else:
                device = user.staticdevice_set.create(id=device_id + 1)
                device.token_set.create(token=username + '1')
                device.token_set.create(token=username + '1')
                device.token_set.create(token=username + '2')

    def test_empty(self):
        data = {}
        form = OTPAuthenticationForm(None, data)

        self.assertTrue(not form.is_valid())
        self.assertEqual(form.get_user(), None)

    def test_bad_password(self):
        data = {
            'username': 'alice',
            'password': 'bogus',
        }
        form = OTPAuthenticationForm(None, data)

        self.assertTrue(not form.is_valid())
        self.assertTrue(form.get_user() is None)
        self.assertEqual(list(form.errors.keys()), ['__all__'])

    def test_no_token(self):
        data = {
            'username': 'alice',
            'password': 'password',
        }
        form = OTPAuthenticationForm(None, data)

        self.assertTrue(not form.is_valid())
        self.assertTrue(form.get_user().get_username() == 'alice')

    def test_passive_token(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_token': 'alice1',
        }
        form = OTPAuthenticationForm(None, data)

        self.assertTrue(form.is_valid())
        alice = form.get_user()
        self.assertTrue(alice.get_username() == 'alice')
        self.assertTrue(isinstance(alice.otp_device, StaticDevice))
        self.assertEqual(alice.otp_device.token_set.count(), 2)

    def test_spoofed_device(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_device': 'django_otp.plugins.otp_static.models.StaticDevice/2',
            'otp_token': 'bob1',
        }
        form = OTPAuthenticationForm(None, data)

        self.assertTrue(not form.is_valid())
        alice = form.get_user()
        self.assertTrue(alice.get_username() == 'alice')
        self.assertTrue(alice.otp_device is None)

    def test_specific_device_fail(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_device': 'django_otp.plugins.otp_email.models.StaticDevice/1',
            'otp_token': 'bogus',
        }
        form = OTPAuthenticationForm(None, data)

        self.assertTrue(not form.is_valid())
        alice = form.get_user()
        self.assertTrue(alice.get_username() == 'alice')
        self.assertTrue(alice.otp_device is None)

    def test_specific_device(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_device': 'django_otp.plugins.otp_static.models.StaticDevice/1',
            'otp_token': 'alice1',
        }
        form = OTPAuthenticationForm(None, data)

        self.assertTrue(form.is_valid())
        alice = form.get_user()
        self.assertTrue(alice.get_username() == 'alice')
        self.assertTrue(alice.otp_device is not None)
