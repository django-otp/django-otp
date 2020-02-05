from datetime import timedelta
from urllib.parse import parse_qs, urlsplit

from freezegun import freeze_time

from django.db import IntegrityError
from django.test.utils import override_settings

from django_otp.forms import OTPAuthenticationForm
from django_otp.models import VerifyNotAllowed
from django_otp.tests import TestCase


class HOTPTest(TestCase):
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

    def test_delay_imposed_after_fail(self):
        ok1 = self.device.verify_token(123456)
        self.assertFalse(ok1)
        ok2 = self.device.verify_token(self.tokens[0])
        self.assertFalse(ok2)

    def test_delay_after_fail_expires(self):
        ok1 = self.device.verify_token(123456)
        self.assertFalse(ok1)
        with freeze_time() as frozen_time:
            # With default settings initial delay is 1 second
            frozen_time.tick(delta=timedelta(seconds=1.1))
            ok2 = self.device.verify_token(self.tokens[0])
            self.assertTrue(ok2)

    def test_throttling_failure_count(self):
        self.assertEqual(self.device.throttling_failure_count, 0)
        for i in range(0, 5):
            self.device.verify_token(123456)
            # Only the first attempt will increase throttling_failure_count,
            # the others will all be within 1 second of first
            # and therefore not count as attempts.
            self.assertEqual(self.device.throttling_failure_count, 1)

    def test_verify_is_allowed(self):
        # Initially should be allowed
        verify_is_allowed1, data1 = self.device.verify_is_allowed()
        self.assertEqual(verify_is_allowed1, True)
        self.assertEqual(data1, None)

        # After failure, verify is not allowed
        self.device.verify_token(123456)
        verify_is_allowed2, data2 = self.device.verify_is_allowed()
        self.assertEqual(verify_is_allowed2, False)
        self.assertEqual(data2, {'reason': VerifyNotAllowed.N_FAILED_ATTEMPTS,
                                 'failure_count': 1})

        # After a successful attempt, should be allowed again
        with freeze_time() as frozen_time:
            frozen_time.tick(delta=timedelta(seconds=1.1))
            self.device.verify_token(self.tokens[0])
            verify_is_allowed3, data3 = self.device.verify_is_allowed()
            self.assertEqual(verify_is_allowed3, True)
            self.assertEqual(data3, None)

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
