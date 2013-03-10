from django.test import TestCase

from django_otp.forms import OTPAuthenticationForm
from .models import TestUser


class AuthFormTest(TestCase):
    fixtures = ['alice_and_bob.yaml']

    def test_custom_user(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_device': 'django_otp.plugins.otp_static.models.StaticDevice/1',
            'otp_token': 'alice1',
        }
        form = OTPAuthenticationForm(None, data)

        self.assert_(form.is_valid())
        alice = form.get_user()
        self.assert_(isinstance(alice, TestUser))
        if hasattr(alice, 'get_username'):
            self.assertEqual(alice.get_username(), 'alice')
        else:
            self.assertEqual(alice.username, 'alice')
        self.assert_(alice.otp_device is not None)
