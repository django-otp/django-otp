#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='django-otp',
    version='0.3.8',
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
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
