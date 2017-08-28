from __future__ import absolute_import, division, print_function, unicode_literals

import pickle
from doctest import DocTestSuite

import django
from django.db import IntegrityError
import django.test

from django_otp import oath
from django_otp import util
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.middleware import OTPMiddleware

if django.VERSION < (1, 7):
    from django.utils import unittest
else:
    import unittest


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()

    suite.addTests(tests)
    suite.addTest(DocTestSuite(util))
    suite.addTest(DocTestSuite(oath))

    return suite


class TestCase(django.test.TestCase):
    """
    Utilities for dealing with custom user models.
    """
    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()

        try:
            from django.contrib.auth import get_user_model
        except ImportError:
            from django.contrib.auth.models import User
            cls.User = User
            cls.User.get_username = lambda self: self.username
            cls.USERNAME_FIELD = 'username'
        else:
            cls.User = get_user_model()
            cls.USERNAME_FIELD = cls.User.USERNAME_FIELD

    def create_user(self, username, password):
        """
        Try to create a user, honoring the custom user model, if any.

        This may raise an exception if the user model is too exotic for our
        purposes.
        """
        return self.User.objects.create_user(username, password=password)


class OTPMiddlewareTestCase(TestCase):
    def setUp(self):
        self.factory = django.test.RequestFactory()
        try:
            self.alice = self.create_user('alice', 'password')
            self.bob = self.create_user('bob', 'password')
        except IntegrityError:
            self.skipTest("Unable to create a test user.")
        else:
            for user in [self.alice, self.bob]:
                device = user.staticdevice_set.create()
                device.token_set.create(token=user.get_username())

        self.middleware = OTPMiddleware()

    def test_verified(self):
        request = self.factory.get('/')
        request.user = self.alice
        device = self.alice.staticdevice_set.get()
        request.session = {
            DEVICE_ID_SESSION_KEY: device.persistent_id
        }

        self.middleware.process_request(request)

        self.assertTrue(request.user.is_verified())

    def test_verified_legacy_device_id(self):
        request = self.factory.get('/')
        request.user = self.alice
        device = self.alice.staticdevice_set.get()
        request.session = {
            DEVICE_ID_SESSION_KEY: '{}.{}/{}'.format(
                device.__module__, device.__class__.__name__, device.id
            )
        }

        self.middleware.process_request(request)

        self.assertTrue(request.user.is_verified())

    def test_unverified(self):
        request = self.factory.get('/')
        request.user = self.alice
        request.session = {}

        self.middleware.process_request(request)

        self.assertFalse(request.user.is_verified())

    def test_no_device(self):
        request = self.factory.get('/')
        request.user = self.alice
        request.session = {
            DEVICE_ID_SESSION_KEY: 'otp_static.staticdevice/0',
        }

        self.middleware.process_request(request)

        self.assertFalse(request.user.is_verified())

    def test_no_model(self):
        request = self.factory.get('/')
        request.user = self.alice
        request.session = {
            DEVICE_ID_SESSION_KEY: 'otp_bogus.bogusdevice/0',
        }

        self.middleware.process_request(request)

        self.assertFalse(request.user.is_verified())

    def test_wrong_user(self):
        request = self.factory.get('/')
        request.user = self.alice
        device = self.bob.staticdevice_set.get()
        request.session = {
            DEVICE_ID_SESSION_KEY: device.persistent_id
        }

        self.middleware.process_request(request)

        self.assertFalse(request.user.is_verified())

    def test_pickling(self):
        request = self.factory.get('/')
        request.user = self.alice
        device = self.alice.staticdevice_set.get()
        request.session = {
            DEVICE_ID_SESSION_KEY: device.persistent_id
        }

        self.middleware.process_request(request)

        # Should not raise an exception.
        pickle.dumps(request.user)
