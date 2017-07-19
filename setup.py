#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='django-otp',
    version='0.4.0',
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
        'django >= 1.8'
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
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
