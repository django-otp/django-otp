from datetime import timedelta
from urllib.parse import parse_qs, urlsplit

from freezegun import freeze_time

from django.db import IntegrityError
from django.test.utils import override_settings

from django_otp.forms import OTPAuthenticationForm
from django_otp.tests import TestCase, ThrottlingTestMixin


class HOTPDeviceMixin:
    """
    A TestCase helper that gives us a HOTPDevice to work with.
    """
    # The next three tokens
    tokens = [782373, 313268, 307722]
    key = 'd2e8a68036f68960b1c30532bb6c56da5934d879'

    def setUp(self):
        try:
            alice = self.create_user(
                'alice', 'password', email='alice@example.com')
        except IntegrityError:
            self.skipTest("Unable to create test user.")
        else:
            self.device = alice.hotpdevice_set.create(
                key=self.key, digits=6,
                tolerance=1, counter=0
            )


@override_settings(
    OTP_HOTP_THROTTLE_FACTOR=0,
)
class HOTPTest(HOTPDeviceMixin, TestCase):
    def test_normal(self):
        ok = self.device.verify_token(self.tokens[0])

        self.assertTrue(ok)
        self.assertEqual(self.device.counter, 1)

    def test_normal_drift(self):
        ok = self.device.verify_token(self.tokens[1])

        self.assertTrue(ok)
        self.assertEqual(self.device.counter, 2)

    def test_excessive_drift(self):
        ok = self.device.verify_token(self.tokens[2])

        self.assertFalse(ok)
        self.assertEqual(self.device.counter, 0)

    def test_bad_value(self):
        ok = self.device.verify_token(123456)

        self.assertFalse(ok)
        self.assertEqual(self.device.counter, 0)

    def test_config_url_no_issuer(self):
        with override_settings(OTP_HOTP_ISSUER=None):
            url = self.device.config_url

        parsed = urlsplit(url)
        params = parse_qs(parsed.query)

        self.assertEqual(parsed.scheme, 'otpauth')
        self.assertEqual(parsed.netloc, 'hotp')
        self.assertEqual(parsed.path, '/alice')
        self.assertIn('secret', params)
        self.assertNotIn('issuer', params)

    def test_config_url_issuer(self):
        with override_settings(OTP_HOTP_ISSUER='example.com'):
            url = self.device.config_url

        parsed = urlsplit(url)
        params = parse_qs(parsed.query)

        self.assertEqual(parsed.scheme, 'otpauth')
        self.assertEqual(parsed.netloc, 'hotp')
        self.assertEqual(parsed.path, '/example.com%3Aalice')
        self.assertIn('secret', params)
        self.assertIn('issuer', params)
        self.assertEqual(params['issuer'][0], 'example.com')

    def test_config_url_issuer_spaces(self):
        with override_settings(OTP_HOTP_ISSUER='Very Trustworthy Source'):
            url = self.device.config_url

        parsed = urlsplit(url)
        params = parse_qs(parsed.query)

        self.assertEqual(parsed.scheme, 'otpauth')
        self.assertEqual(parsed.netloc, 'hotp')
        self.assertEqual(parsed.path, '/Very%20Trustworthy%20Source%3Aalice')
        self.assertIn('secret', params)
        self.assertIn('issuer', params)
        self.assertEqual(params['issuer'][0], 'Very Trustworthy Source')

    def test_config_url_issuer_method(self):
        with override_settings(OTP_HOTP_ISSUER=lambda d: d.user.email):
            url = self.device.config_url

        parsed = urlsplit(url)
        params = parse_qs(parsed.query)

        self.assertEqual(parsed.scheme, 'otpauth')
        self.assertEqual(parsed.netloc, 'hotp')
        self.assertEqual(parsed.path, '/alice%40example.com%3Aalice')
        self.assertIn('secret', params)
        self.assertIn('issuer', params)
        self.assertEqual(params['issuer'][0], 'alice@example.com')


class AuthFormTest(TestCase):
    """
    Test auth form with HOTP tokens
    """
    tokens = HOTPTest.tokens
    key = HOTPTest.key

    def setUp(self):
        try:
            alice = self.create_user('alice', 'password')
        except IntegrityError:
            self.skipTest("Unable to create test user.")
        else:
            self.device = alice.hotpdevice_set.create(
                key=self.key, digits=6,
                tolerance=1, counter=0
            )

    def test_no_token(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_device': self.device.persistent_id,
        }
        form = OTPAuthenticationForm(None, data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.get_user().get_username(), 'alice')

    def test_bad_token(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_token': '123456',
            'otp_device': self.device.persistent_id,
        }
        form = OTPAuthenticationForm(None, data)
        self.assertFalse(form.is_valid())

    def test_good_token(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_token': self.tokens[0],
            'otp_device': self.device.persistent_id,
        }
        form = OTPAuthenticationForm(None, data)
        self.assertTrue(form.is_valid())

    def test_attempt_after_fail(self):
        good_data = {
            'username': 'alice',
            'password': 'password',
            'otp_token': self.tokens[0],
            'otp_device': self.device.persistent_id,
        }
        bad_data = {
            'username': 'alice',
            'password': 'password',
            'otp_token': '123456',
            'otp_device': self.device.persistent_id,
        }

        with freeze_time() as frozen_time:
            form1 = OTPAuthenticationForm(None, bad_data)
            self.assertFalse(form1.is_valid())

            # Should fail even with good data:
            form2 = OTPAuthenticationForm(None, good_data)
            self.assertFalse(form2.is_valid())
            self.assertIn('Verification temporarily disabled because of 1 failed attempt', form2.errors['__all__'][0])

            # Fail again after throttling expired:
            frozen_time.tick(timedelta(seconds=1.1))
            form3 = OTPAuthenticationForm(None, bad_data)
            self.assertFalse(form3.is_valid())
            self.assertIn('Invalid token', form3.errors['__all__'][0])

            # Test n=2 error message:
            form4 = OTPAuthenticationForm(None, bad_data)
            self.assertFalse(form4.is_valid())
            self.assertIn('Verification temporarily disabled because of 2 failed attempts', form4.errors['__all__'][0])

            # Pass this time:
            frozen_time.tick(timedelta(seconds=2.1))
            form5 = OTPAuthenticationForm(None, good_data)
            self.assertTrue(form5.is_valid())


@override_settings(
    OTP_HOTP_THROTTLE_FACTOR=1,
)
class ThrottlingTestCase(HOTPDeviceMixin, ThrottlingTestMixin, TestCase):
    def valid_token(self):
        return self.tokens[0]

    def invalid_token(self):
        return -1
