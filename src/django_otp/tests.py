from doctest import DocTestSuite
from io import StringIO
import pickle
from threading import Thread
import unittest

from django.contrib.auth.models import AnonymousUser
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, connection
from django.test import AsyncRequestFactory, RequestFactory, skipUnlessDBFeature
from django.test.utils import override_settings
from django.urls import reverse

from django_otp import (
    DEVICE_ID_SESSION_KEY,
    device_classes,
    match_token,
    oath,
    user_has_device,
    util,
    verify_token,
)
from django_otp.forms import OTPTokenForm, otp_verification_failed
from django_otp.middleware import OTPMiddleware
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken

from .test_utils import TestCase, TransactionTestCase


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()

    suite.addTests(tests)
    suite.addTest(DocTestSuite(util))
    suite.addTest(DocTestSuite(oath))

    return suite


class TestThread(Thread):
    "Django testing quirk: threads have to close their DB connections."

    def run(self):
        super().run()
        connection.close()


@override_settings(OTP_STATIC_THROTTLE_FACTOR=0)
class APITestCase(TestCase):
    def setUp(self):
        try:
            self.alice = self.create_user('alice', 'password')
            self.bob = self.create_user('bob', 'password')
        except IntegrityError:
            self.skipTest("Unable to create a test user.")
        else:
            device = self.alice.staticdevice_set.create()
            device.token_set.create(token='alice')

    def test_user_has_device(self):
        with self.subTest(user='anonymous'):
            self.assertFalse(user_has_device(AnonymousUser()))
        with self.subTest(user='alice'):
            self.assertTrue(user_has_device(self.alice))
        with self.subTest(user='bob'):
            self.assertFalse(user_has_device(self.bob))

    def test_verify_token(self):
        device = self.alice.staticdevice_set.first()

        verified = verify_token(self.alice, device.persistent_id, 'bogus')
        self.assertIsNone(verified)

        verified = verify_token(self.alice, device.persistent_id, 'alice')
        self.assertIsNotNone(verified)

    def test_match_token(self):
        verified = match_token(self.alice, 'bogus')
        self.assertIsNone(verified)

        verified = match_token(self.alice, 'alice')
        self.assertEqual(verified, self.alice.staticdevice_set.first())

    def test_device_classes(self):
        classes = list(device_classes())

        self.assertFalse(any(model._meta.proxy for model in classes))


class OTPVerificationFailedSignalTestCase(TestCase):
    def setUp(self):
        try:
            self.alice = self.create_user('alice', 'password')
        except IntegrityError:
            self.skipTest("Unable to create a test user.")
        else:
            self.device = self.alice.staticdevice_set.create()
            self.device.token_set.create(token='valid')

        self.signal_received = False
        otp_verification_failed.connect(self.signal_handler)

    def tearDown(self):
        otp_verification_failed.disconnect(self.signal_handler)

    def signal_handler(self, sender, **kwargs):
        self.signal_received = True

    def test_otp_verification_failed_signal(self):
        form = OTPTokenForm(
            self.alice,
            None,
            {'otp_device': self.device.persistent_id, 'otp_token': 'invalid'},
        )
        form.is_valid()
        self.assertTrue(
            self.signal_received, "otp_verification_failed signal was not emitted."
        )


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
        request.session = {DEVICE_ID_SESSION_KEY: device.persistent_id}

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
        request.session = {DEVICE_ID_SESSION_KEY: device.persistent_id}

        self.middleware(request)

        self.assertFalse(request.user.is_verified())

    def test_pickling(self):
        request = self.factory.get('/')
        request.user = self.alice
        device = self.alice.staticdevice_set.get()
        request.session = {DEVICE_ID_SESSION_KEY: device.persistent_id}

        self.middleware(request)

        # Should not raise an exception.
        pickle.dumps(request.user)


class OTPMiddlewareAsyncTestCase(TestCase):
    def setUp(self):
        self.factory = AsyncRequestFactory()

        try:
            self.alice = self.create_user("alice", "password")
            self.bob = self.create_user("bob", "password")
        except IntegrityError:
            self.skipTest("Unable to create a test user.")
        else:
            for user in (self.alice, self.bob):
                device = user.staticdevice_set.create()
                device.token_set.create(token=user.get_username())

        # Precompute anything that would otherwise hit the (sync) ORM inside async tests.
        alice_device = self.alice.staticdevice_set.get()
        bob_device = self.bob.staticdevice_set.get()

        self.alice_device_pid = alice_device.persistent_id
        self.bob_device_pid = bob_device.persistent_id
        self.alice_device_legacy_pid = "{}.{}/{}".format(
            alice_device.__module__, alice_device.__class__.__name__, alice_device.id
        )

        async def get_response(request):
            return None

        self.middleware = OTPMiddleware(get_response)

    async def _run_middleware(self, user, session):
        request = self.factory.get("/")
        request.session = session
        request.user = user

        async def auser():
            return user

        request.auser = auser

        await self.middleware(request)
        return request

    async def test_verified(self):
        request = await self._run_middleware(
            self.alice, {DEVICE_ID_SESSION_KEY: self.alice_device_pid}
        )

        user = await request.auser()
        self.assertTrue(user.is_verified())

    async def test_verified_legacy_device_id(self):
        request = await self._run_middleware(
            self.alice, {DEVICE_ID_SESSION_KEY: self.alice_device_legacy_pid}
        )

        user = await request.auser()
        self.assertTrue(user.is_verified())

    async def test_unverified(self):
        request = await self._run_middleware(self.alice, {})

        user = await request.auser()
        self.assertFalse(user.is_verified())

    async def test_no_device(self):
        request = await self._run_middleware(
            self.alice, {DEVICE_ID_SESSION_KEY: "otp_static.staticdevice/0"}
        )

        user = await request.auser()
        self.assertFalse(user.is_verified())

    async def test_no_model(self):
        request = await self._run_middleware(
            self.alice, {DEVICE_ID_SESSION_KEY: "otp_bogus.bogusdevice/0"}
        )

        user = await request.auser()
        self.assertFalse(user.is_verified())

    async def test_wrong_user(self):
        request = await self._run_middleware(
            self.alice, {DEVICE_ID_SESSION_KEY: self.bob_device_pid}
        )

        user = await request.auser()
        self.assertFalse(user.is_verified())

    async def test_pickling(self):
        request = await self._run_middleware(
            self.alice, {DEVICE_ID_SESSION_KEY: self.alice_device_pid}
        )

        user = await request.auser()
        # Should not raise an exception.
        pickle.dumps(user)


class LoginViewTestCase(TestCase):
    def setUp(self):
        try:
            self.alice = self.create_user('alice', 'password')
            self.bob = self.create_user('bob', 'password', is_staff=True)
        except IntegrityError:
            self.skipTest("Unable to create a test user.")
        else:
            for user in [self.alice, self.bob]:
                device = user.staticdevice_set.create()
                device.token_set.create(token=user.get_username())

    def test_admin_login_template(self):
        response = self.client.get(reverse('otpadmin:login'))
        self.assertContains(response, 'Username:')
        self.assertContains(response, 'Password:')
        self.assertNotContains(response, 'OTP Device:')
        self.assertContains(response, 'OTP Token:')
        response = self.client.post(
            reverse('otpadmin:login'),
            data={
                'username': self.bob.get_username(),
                'password': 'password',
            },
        )
        self.assertContains(response, 'Username:')
        self.assertContains(response, 'Password:')
        self.assertContains(response, 'OTP Device:')
        self.assertContains(response, 'OTP Token:')

        device = self.bob.staticdevice_set.get()
        token = device.token_set.get()
        response = self.client.post(
            reverse('otpadmin:login'),
            data={
                'username': self.bob.get_username(),
                'password': 'password',
                'otp_device': device.persistent_id,
                'otp_token': token.token,
                'next': '/',
            },
        )
        self.assertRedirects(response, '/')

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

        response = self.client.post(reverse('login'), params)
        self.assertRedirects(response, '/')

        response = self.client.get('/')
        self.assertInHTML(
            f'<span id="username">{self.alice.get_username()}</span>',
            response.content.decode(response.charset),
        )

    def test_verify(self):
        device = self.alice.staticdevice_set.get()
        token = device.token_set.get()

        params = {
            'otp_device': device.persistent_id,
            'otp_token': token.token,
            'next': '/',
        }

        self.client.login(username=self.alice.get_username(), password='password')

        response = self.client.post(reverse('login-otp'), params)
        self.assertRedirects(response, '/')

        response = self.client.get('/')
        self.assertInHTML(
            f'<span id="username">{self.alice.get_username()}</span>',
            response.content.decode(response.charset),
        )


@skipUnlessDBFeature('has_select_for_update')
@override_settings(OTP_STATIC_THROTTLE_FACTOR=0)
class ConcurrencyTestCase(TransactionTestCase):
    def setUp(self):
        try:
            self.alice = self.create_user('alice', 'password')
            self.bob = self.create_user('bob', 'password')
        except IntegrityError:
            self.skipTest("Unable to create a test user.")
        else:
            for user in [self.alice, self.bob]:
                device = user.staticdevice_set.create()
                device.token_set.create(token='valid')

    def test_verify_token(self):
        class VerifyThread(Thread):
            def __init__(self, user, device_id, token):
                super().__init__()

                self.user = user
                self.device_id = device_id
                self.token = token

                self.verified = None

            def run(self):
                self.verified = verify_token(self.user, self.device_id, self.token)
                connection.close()

        device = self.alice.staticdevice_set.get()
        threads = [
            VerifyThread(device.user, device.persistent_id, 'valid') for _ in range(10)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(sum(1 for t in threads if t.verified is not None), 1)

    def test_match_token(self):
        class VerifyThread(Thread):
            def __init__(self, user, token):
                super().__init__()

                self.user = user
                self.token = token

                self.verified = None

            def run(self):
                self.verified = match_token(self.user, self.token)
                connection.close()

        threads = [VerifyThread(self.alice, 'valid') for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(sum(1 for t in threads if t.verified is not None), 1)

    def test_concurrent_throttle_count(self):
        self._test_throttling_concurrency(thread_count=10, expected_failures=10)

    @override_settings(OTP_STATIC_THROTTLE_FACTOR=1)
    def test_serialized_throttling(self):
        # After the first failure, verification will be skipped and the count
        # will not be incremented.
        self._test_throttling_concurrency(thread_count=10, expected_failures=1)

    def _test_throttling_concurrency(self, thread_count, expected_failures):
        forms = (
            OTPTokenForm(
                device.user,
                None,
                {'otp_device': device.persistent_id, 'otp_token': 'bogus'},
            )
            for _ in range(thread_count)
            for device in StaticDevice.objects.all()
        )

        threads = [TestThread(target=form.is_valid) for form in forms]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        for device in StaticDevice.objects.all():
            with self.subTest(user=device.user.get_username()):
                self.assertEqual(device.throttling_failure_count, expected_failures)


class AddStaticTokenTestCase(TestCase):
    def setUp(self):
        try:
            self.alice = self.create_user('alice', 'password')
            self.bob = self.create_user('bob', 'password', is_staff=True)
        except IntegrityError:
            self.skipTest("Unable to create a test user.")

    def test_no_user(self):
        with self.assertRaises(CommandError):
            call_command('addstatictoken', 'bogus')

    def test_new_device(self):
        out = StringIO()
        call_command('addstatictoken', 'alice', stdout=out)
        token = out.getvalue().strip()

        static_token = StaticToken.objects.select_related('device__user').get(
            token=token
        )
        self.assertEqual(static_token.device.user, self.alice)

    def test_existing_device(self):
        device = self.alice.staticdevice_set.create()

        out = StringIO()
        call_command('addstatictoken', 'alice', stdout=out)
        token = out.getvalue().strip()

        static_token = StaticToken.objects.select_related('device__user').get(
            token=token
        )
        self.assertEqual(static_token.device, device)

    def test_explicit_token(self):
        device = self.alice.staticdevice_set.create()

        out = StringIO()
        call_command('addstatictoken', 'alice', '-t', 'secret-token', stdout=out)
        token = out.getvalue().strip()

        static_token = StaticToken.objects.select_related('device__user').get(
            token=token
        )
        self.assertEqual(token, 'secret-token')
        self.assertEqual(static_token.device, device)
