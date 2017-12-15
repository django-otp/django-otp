from __future__ import absolute_import, division, print_function, unicode_literals

from django.db import IntegrityError

from django_otp.forms import OTPAuthenticationForm
from django_otp.tests import TestCase

from .lib import add_static_token
from .models import StaticDevice


class DeviceTest(TestCase):
    """ A few generic tests to get us started. """
    def setUp(self):
        try:
            self.user = self.create_user('alice', 'password')
        except Exception:
            self.skipTest("Unable to create the test user.")

    def test_str(self):
        device = StaticDevice.objects.create(user=self.user, name="Device")

        str(device)

    def test_str_unpopulated(self):
        device = StaticDevice()

        str(device)


class LibTest(TestCase):
    """
    Test miscellaneous library functions.
    """
    def setUp(self):
        try:
            self.user = self.create_user('alice', 'password')
        except Exception:
            self.skipTest("Unable to create the test user.")

    def test_add_static_token(self):
        statictoken = add_static_token('alice')

        self.assertEqual(statictoken.device.user, self.user)
        self.assertEqual(self.user.staticdevice_set.count(), 1)

    def test_add_static_token_existing_device(self):
        self.user.staticdevice_set.create(name='Test')
        statictoken = add_static_token('alice')

        self.assertEqual(statictoken.device.user, self.user)
        self.assertEqual(self.user.staticdevice_set.count(), 1)
        self.assertEqual(statictoken.device.name, 'Test')

    def test_add_static_token_no_user(self):
        with self.assertRaises(self.User.DoesNotExist):
            add_static_token('bogus')

    def test_add_static_token_specific(self):
        statictoken = add_static_token('alice', 'token')

        self.assertEqual(statictoken.token, 'token')


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

        self.assertFalse(form.is_valid())
        self.assertEqual(form.get_user(), None)

    def test_bad_password(self):
        data = {
            'username': 'alice',
            'password': 'bogus',
        }
        form = OTPAuthenticationForm(None, data)

        self.assertFalse(form.is_valid())
        self.assertEqual(list(form.errors.keys()), ['__all__'])

    def test_no_token(self):
        data = {
            'username': 'alice',
            'password': 'password',
        }
        form = OTPAuthenticationForm(None, data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.get_user().get_username(), 'alice')

    def test_passive_token(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_token': 'alice1',
        }
        form = OTPAuthenticationForm(None, data)

        self.assertTrue(form.is_valid())
        alice = form.get_user()
        self.assertEqual(alice.get_username(), 'alice')
        self.assertIsInstance(alice.otp_device, StaticDevice)
        self.assertEqual(alice.otp_device.token_set.count(), 2)

    def test_spoofed_device(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_device': 'otp_static.staticdevice/2',
            'otp_token': 'bob1',
        }
        form = OTPAuthenticationForm(None, data)

        self.assertFalse(form.is_valid())
        alice = form.get_user()
        self.assertEqual(alice.get_username(), 'alice')
        self.assertIsNone(alice.otp_device)

    def test_specific_device_fail(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_device': 'otp_email.staticdevice/1',
            'otp_token': 'bogus',
        }
        form = OTPAuthenticationForm(None, data)

        self.assertFalse(form.is_valid())
        alice = form.get_user()
        self.assertEqual(alice.get_username(), 'alice')
        self.assertIsNone(alice.otp_device)

    def test_specific_device(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_device': 'otp_static.staticdevice/1',
            'otp_token': 'alice1',
        }
        form = OTPAuthenticationForm(None, data)

        self.assertTrue(form.is_valid())
        alice = form.get_user()
        self.assertEqual(alice.get_username(), 'alice')
        self.assertIsNotNone(alice.otp_device)
