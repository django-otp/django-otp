#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='django-otp',
    version='0.6.0',
    description='A pluggable framework for adding two-factor authentication to Django using one-time passwords.',
    long_description=open('README.rst').read(),
    author='Peter Sagerson',
    author_email='psagers@ignorare.net',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    url='https://bitbucket.org/psagers/django-otp',
    license='BSD',
    install_requires=[
        'django >= 1.11'
    ],
    extras_require={
        'qrcode': ['qrcode'],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
