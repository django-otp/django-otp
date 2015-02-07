#!/usr/bin/env python

from __future__ import print_function
from os import walk

from setuptools import setup, find_packages


# Automatically include all package data
with open('MANIFEST.in', 'w') as manifest:
    print('include README.rst CHANGES LICENSE', file=manifest)
    print('recursive-include docs *.rst *.py Makefile', file=manifest)
    print('prune docs/build', file=manifest)

    for dirpath, dirnames, filenames in walk('django_otp'):
        if not dirpath.endswith('__pycache__'):
            if (len(filenames) > 0) and ('__init__.py' not in filenames):
                print('recursive-include {0} *'.format(dirpath), file=manifest)
                dirnames[:] = []


setup(
    name='django-otp',
    version='0.2.7',
    description='A pluggable framework for adding two-factor authentication to Django using one-time passwords.',
    long_description=open('README.rst').read(),
    author='Peter Sagerson',
    author_email='psagersDjwublJf@ignorare.net',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    url='https://bitbucket.org/psagers/django-otp',
    license='BSD',
    install_requires=[
        'django >= 1.4.2'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
    ],
)
