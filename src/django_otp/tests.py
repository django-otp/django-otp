from doctest import DocTestSuite
import pickle
import unittest

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import RequestFactory, TestCase as DjangoTestCase

from django_otp import DEVICE_ID_SESSION_KEY, oath, util
from django_otp.middleware import OTPMiddleware


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()

    suite.addTests(tests)
    suite.addTest(DocTestSuite(util))
    suite.addTest(DocTestSuite(oath))

    return suite


class TestCase(DjangoTestCase):
    """
    Utilities for dealing with custom user models.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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
        self.factory = RequestFactory()
        try:
            self.alice = self.create_user('alice', 'password')
            self.bob = self.create_user('bob', 'password')
        except IntegrityError:
            self.skipTest("Unable to create a test user.")
        else:
            for user in [self.alice, self.bob]:
                device = user.staticdevice_set.create()
                device.token_set.create(token=user.get_username())

        self.middleware = OTPMiddleware(lambda r: None)

    def test_verified(self):
        request = self.factory.get('/')
        request.user = self.alice
        device = self.alice.staticdevice_set.get()
        request.session = {
            DEVICE_ID_SESSION_KEY: device.persistent_id
        }

        self.middleware(request)

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

        self.middleware(request)

        self.assertTrue(request.user.is_verified())

    def test_unverified(self):
        request = self.factory.get('/')
        request.user = self.alice
        request.session = {}

        self.middleware(request)

        self.assertFalse(request.user.is_verified())

    def test_no_device(self):
        request = self.factory.get('/')
        request.user = self.alice
        request.session = {
            DEVICE_ID_SESSION_KEY: 'otp_static.staticdevice/0',
        }

        self.middleware(request)

        self.assertFalse(request.user.is_verified())

    def test_no_model(self):
        request = self.factory.get('/')
        request.user = self.alice
        request.session = {
            DEVICE_ID_SESSION_KEY: 'otp_bogus.bogusdevice/0',
        }

        self.middleware(request)

        self.assertFalse(request.user.is_verified())

    def test_wrong_user(self):
        request = self.factory.get('/')
        request.user = self.alice
        device = self.bob.staticdevice_set.get()
        request.session = {
            DEVICE_ID_SESSION_KEY: device.persistent_id
        }

        self.middleware(request)

        self.assertFalse(request.user.is_verified())

    def test_pickling(self):
        request = self.factory.get('/')
        request.user = self.alice
        device = self.alice.staticdevice_set.get()
        request.session = {
            DEVICE_ID_SESSION_KEY: device.persistent_id
        }

        self.middleware(request)

        # Should not raise an exception.
        pickle.dumps(request.user)


class LoginViewTestCase(TestCase):
    def setUp(self):
        try:
            self.alice = self.create_user('alice', 'password')
            self.bob = self.create_user('bob', 'password')
        except IntegrityError:
            self.skipTest("Unable to create a test user.")
        else:
            for user in [self.alice, self.bob]:
                device = user.staticdevice_set.create()
                device.token_set.create(token=user.get_username())

    def test_authenticate(self):
        device = self.alice.staticdevice_set.get()
        token = device.token_set.get()

        params = {
            'username': self.alice.get_username(),
            'password': 'password',
            'otp_device': device.persistent_id,
            'otp_token': token.token,
            'next': '/',
        }

        response = self.client.post('/login/', params)
        self.assertRedirects(response, '/')

        response = self.client.get('/')
        self.assertContains(response, self.alice.get_username())

    def test_verify(self):
        device = self.alice.staticdevice_set.get()
        token = device.token_set.get()

        params = {
            'otp_device': device.persistent_id,
            'otp_token': token.token,
            'next': '/',
        }

        self.client.login(username=self.alice.get_username(), password='password')

        response = self.client.post('/login/', params)
        self.assertRedirects(response, '/')

        response = self.client.get('/')
        self.assertContains(response, self.alice.get_username())
