from django.test import TestCase

from .models import HOTPDevice


class HOTPTest(TestCase):
    fixtures = ['tests/hotp']

    # The next three tokens
    tokens = [782373, 313268, 307722]

    def setUp(self):
        self.device = HOTPDevice.objects.get()

    def test_normal(self):
        ok = self.device.verify_token(self.tokens[0])

        self.assert_(ok)
        self.assertEqual(self.device.counter, 1)

    def test_normal_drift(self):
        ok = self.device.verify_token(self.tokens[1])

        self.assert_(ok)
        self.assertEqual(self.device.counter, 2)

    def test_excessive_drift(self):
        ok = self.device.verify_token(self.tokens[2])

        self.assert_(not ok)
        self.assertEqual(self.device.counter, 0)

    def test_bad_value(self):
        ok = self.device.verify_token(123456)

        self.assert_(not ok)
        self.assertEqual(self.device.counter, 0)
