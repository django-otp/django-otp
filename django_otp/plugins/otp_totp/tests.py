from time import time

from django.test import TestCase

from .models import TOTPDevice
from .conf import settings


class TOTPTest(TestCase):
    fixtures = ['tests/totp']

    # The next ten tokens
    tokens = [179225, 656163, 839400, 154567, 346912, 471576, 45675, 101397, 491039, 784503]

    def setUp(self):
        """
        Load the device and move it to the fourth time step. The current token
        is 154567.
        """
        settings.OTP_OATH_TOTP_SYNC = False
        self.device = TOTPDevice.objects.get()
        self.device.t0 = int(time() - (30 * 3))

    def test_single(self):
        results = [self.device.verify_token(token) for token in self.tokens]

        self.assertEqual(results, [False]*3 + [True] + [False]*6)

    def test_tolerance(self):
        self.device.tolerance = 1
        results = [self.device.verify_token(token) for token in self.tokens]

        self.assertEqual(results, [False]*2 + [True]*3 + [False]*5)

    def test_drift(self):
        self.device.tolerance = 1
        self.device.drift = -1
        results = [self.device.verify_token(token) for token in self.tokens]

        self.assertEqual(results, [False]*1 + [True]*3 + [False]*6)

    def test_sync_drift(self):
        settings.OTP_OATH_TOTP_SYNC = True
        self.device.tolerance = 2
        ok = self.device.verify_token(self.tokens[5])

        self.assert_(ok)
        self.assertEqual(self.device.drift, 2)

    def test_sync_results(self):
        self.device.tolerance = 1
        settings.OTP_OATH_TOTP_SYNC = True
        self.device.verify_token(self.tokens[4])
        settings.OTP_OATH_TOTP_SYNC = False
        results = [self.device.verify_token(token) for token in self.tokens]

        self.assertEqual(self.device.drift, 1)
        self.assertEqual(results, [False]*3 + [True]*3 + [False]*4)
