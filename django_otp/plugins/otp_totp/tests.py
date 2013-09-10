from time import time

from django.db import IntegrityError

try:
    from django.test.utils import override_settings
except ImportError:
    # Django < 1.4 doesn't have override_settings. Just skip the tests in that
    # case.
    from django.utils.unittest import skip
    override_settings = lambda *args, **kwargs: skip

from django_otp.tests import TestCase


@override_settings(OTP_TOTP_SYNC=False)
class TOTPTest(TestCase):
    # The next ten tokens
    tokens = [179225, 656163, 839400, 154567, 346912, 471576, 45675, 101397, 491039, 784503]

    def setUp(self):
        """
        Create a device at the fourth time step. The current token is 154567.
        """
        try:
            alice = self.create_user('alice', 'password')
        except IntegrityError:
            self.skipTest("Unable to create the test user.")
        else:
            self.device = alice.totpdevice_set.create(
                key='2a2bbba1092ffdd25a328ad1a0a5f5d61d7aacc4', step=30,
                t0=int(time() - (30 * 3)), digits=6, tolerance=0, drift=0
            )

    def test_single(self):
        results = [self.device.verify_token(token) for token in self.tokens]

        self.assertEqual(results, [False] * 3 + [True] + [False] * 6)

    def test_tolerance(self):
        self.device.tolerance = 1
        results = [self.device.verify_token(token) for token in self.tokens]

        self.assertEqual(results, [False] * 2 + [True] * 3 + [False] * 5)

    def test_drift(self):
        self.device.tolerance = 1
        self.device.drift = -1
        results = [self.device.verify_token(token) for token in self.tokens]

        self.assertEqual(results, [False] * 1 + [True] * 3 + [False] * 6)

    def test_sync_drift(self):
        self.device.tolerance = 2
        with self.settings(OTP_TOTP_SYNC=True):
            ok = self.device.verify_token(self.tokens[5])

        self.assertTrue(ok)
        self.assertEqual(self.device.drift, 2)

    def test_sync_results(self):
        self.device.tolerance = 1
        with self.settings(OTP_TOTP_SYNC=True):
            self.device.verify_token(self.tokens[4])
        results = [self.device.verify_token(token) for token in self.tokens]

        self.assertEqual(self.device.drift, 1)
        self.assertEqual(results, [False] * 3 + [True] * 3 + [False] * 4)
