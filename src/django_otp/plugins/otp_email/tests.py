from __future__ import absolute_import, division, print_function, unicode_literals

from django.core import mail
from django.db import IntegrityError
from django.test.utils import override_settings

from django_otp.forms import OTPAuthenticationForm
from django_otp.tests import TestCase
from .models import EmailDevice


class AuthFormTest(TestCase):
    def setUp(self):
        try:
            alice = self.create_user('alice', 'password')
        except IntegrityError:
            self.skipTest("Failed to create user.")
        else:
            alice.emaildevice_set.create()

        if hasattr(alice, 'email'):
            alice.email = 'alice@example.com'
            alice.save()
        else:
            self.skipTest("User model has no email.")

    @override_settings(OTP_EMAIL_SENDER='test@example.com')
    def test_email_interaction(self):
        data = {
            'username': 'alice',
            'password': 'password',
            'otp_device': 'otp_email.emaildevice/1',
            'otp_token': '',
            'otp_challenge': '1',
        }
        form = OTPAuthenticationForm(None, data)

        self.assertFalse(form.is_valid())
        alice = form.get_user()
        self.assertEqual(alice.get_username(), 'alice')
        self.assertIsNone(alice.otp_device)
        self.assertEqual(len(mail.outbox), 1)

        data['otp_token'] = mail.outbox[0].body
        del data['otp_challenge']
        form = OTPAuthenticationForm(None, data)

        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.get_user().otp_device, EmailDevice)
