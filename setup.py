#!/usr/bin/env python

import os
import os.path
import re

from setuptools import find_packages, setup


def gen_package_data(pkg_root, paths, prune=[]):
    """
    Generates a value for package_data.

    pkg_root is the path to the Python package we're generating package_data
    for. paths is a list of paths relative to pkg_root to add. We'll search
    these directories recursively, yielding a sequence of '<sub-path>/*'
    strings to select every nested file for inclusion.

    The optional third argument is a collection of directory names to prune
    from the traversal.

    """
    pkg_root = os.path.abspath(pkg_root)

    # For stripping pkg_root from results.
    root_re = re.compile(r'^' + re.escape(pkg_root) + r'/*')

    for path in paths:
        for dirpath, dirnames, _ in os.walk(os.path.join(pkg_root, path)):
            dirpath = root_re.sub('', dirpath)
            yield os.path.join(dirpath, '*')
            if prune:
                dirnames[:] = [d for d in dirnames if d not in prune]


def find_package_data(*args, **kwargs):
    return list(gen_package_data(*args, **kwargs))


setup(
    name='django-otp',
    version='0.9.1',
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
    package_data={
        'django_otp': find_package_data('src/django_otp', ['templates']),
        'django_otp.plugins.otp_email': find_package_data('src/django_otp/plugins/otp_email', ['templates']),
        'django_otp.plugins.otp_hotp': find_package_data('src/django_otp/plugins/otp_hotp', ['templates']),
        'django_otp.plugins.otp_totp': find_package_data('src/django_otp/plugins/otp_totp', ['templates']),
    },
    zip_safe=False,

    install_requires=[
        'django >= 1.11',
    ],
    extras_require={
        'qrcode': ['qrcode'],
    },
)
