from __future__ import absolute_import, division, print_function, unicode_literals

from django.db import IntegrityError
from django.test.utils import override_settings
from django.utils.six.moves.urllib.parse import urlsplit, parse_qs

from django_otp.tests import TestCase


class HOTPTest(TestCase):
    # The next three tokens
    tokens = [782373, 313268, 307722]

    def setUp(self):
        try:
            alice = self.create_user('alice', 'password')
        except IntegrityError:
            self.skipTest("Unable to create test user.")
        else:
            self.device = alice.hotpdevice_set.create(
                key='d2e8a68036f68960b1c30532bb6c56da5934d879', digits=6,
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
