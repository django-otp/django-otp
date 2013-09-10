from django.db import IntegrityError

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

        self.assertTrue(not ok)
        self.assertEqual(self.device.counter, 0)

    def test_bad_value(self):
        ok = self.device.verify_token(123456)

        self.assertTrue(not ok)
        self.assertEqual(self.device.counter, 0)
