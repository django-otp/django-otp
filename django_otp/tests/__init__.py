from django.utils import unittest
from doctest import DocTestSuite

from django_otp import util
from django_otp import oath

from .forms import AuthFormTest


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTest(DocTestSuite(util))
    suite.addTest(DocTestSuite(oath))
    suite.addTest(loader.loadTestsFromTestCase(AuthFormTest))

    return suite
