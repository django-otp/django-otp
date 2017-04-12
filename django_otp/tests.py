from __future__ import absolute_import, division, print_function, unicode_literals

import pickle
from doctest import DocTestSuite

import django
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
            user = self.create_user('alice', 'password')
        except IntegrityError:
            self.skipTest("Unable to create a test user.")
        else:
            device = user.staticdevice_set.create(id=1)
            device.token_set.create(token='alice1')

    def test_pickling(self):
        middleware = OTPMiddleware()
        request = self.factory.get('/')
        request.user = user = self.User.objects.first()
        device = user.staticdevice_set.first()
        request.session = {
            DEVICE_ID_SESSION_KEY: device.persistent_id
        }
        middleware.process_request(request)

        pickle.dumps(request.user)

