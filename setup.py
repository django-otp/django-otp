#!/usr/bin/env python

from setuptools import find_packages, setup


setup(
    name='django-otp',
    version='1.0.3',
    description="A pluggable framework for adding two-factor authentication to Django using one-time passwords.",
    license='BSD',
    author="Peter Sagerson",
    author_email='psagers@ignorare.net',
    url='https://github.com/django-otp/django-otp',
    project_urls={
        "Documentation": 'https://django-otp-official.readthedocs.io/',
        "Source": 'https://github.com/django-otp/django-otp',
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'django >= 2.2',
    ],
    extras_require={
        'qrcode': ['qrcode'],
    },
)
