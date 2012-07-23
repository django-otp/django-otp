#!/usr/bin/env python

from distutils.core import setup


setup(
    name='django-otp',
    version='0.1.0',
    description='A pluggable framework for adding two-factor authentication to Django using one-time passwords.',
    long_description=open('README').read(),
    author='Peter Sagerson',
    author_email='psagersDjwublJf@ignorare.net',
    packages=[
        'django_otp',
        'django_otp.tests',
        'django_otp.plugins.otp_email',
        'django_otp.plugins.otp_hotp',
        'django_otp.plugins.otp_static',
        'django_otp.plugins.otp_static.management',
        'django_otp.plugins.otp_static.management.commands',
        'django_otp.plugins.otp_totp',
    ],
    url='https://bitbucket.org/psagers/django-otp',
    license='BSD',
    install_requires=[
        'django>=1.3'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
) 
